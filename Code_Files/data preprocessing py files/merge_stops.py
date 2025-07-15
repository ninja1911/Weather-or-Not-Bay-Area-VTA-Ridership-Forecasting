# %%
import polars as pl
import os

# %%
RAW_DATA_FOLDER = "raw_data"
STAGING_DATA_FOLDER = "staging_data"

# %%
ridership = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "Ridership.csv"))
    .select(["Stop Id", "IVR Number"])
    .with_columns(
        pl.col("Stop Id").str.replace_all(",", "").cast(pl.UInt16),
        pl.col("IVR Number").str.replace_all(",", "").cast(pl.UInt32),
    )
    .with_columns(
        pl.when(pl.col("IVR Number").is_null())
        .then(pl.col("Stop Id") + 60000)
        .otherwise(pl.col("IVR Number"))
        .alias("IVR Number")
    )
    .with_columns(
        pl.when(pl.col("IVR Number") < 60000)
        .then(pl.col("Stop Id") + 60000)
        .otherwise(pl.col("IVR Number"))
        .alias("IVR Number")
    )
    .unique()
)

# %%
feb2020lf = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "Feb2020_RBS_Final.csv"))
    .select(["Stop_ID", "LAT_Num", "LON_Num"])
    .with_columns(
        pl.col("Stop_ID").cast(pl.UInt16),
        pl.col("LAT_Num").cast(pl.Float32),
        pl.col("LON_Num").cast(pl.Float32),
    )
    .unique()
)

# %%
oct2022lf = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "RidershipbyStop2022.csv"))
    .select(["Stop ID text", "Lat", "Long"])
    .with_columns(
        pl.col("Stop ID text").cast(pl.UInt32),
        pl.col("Lat").cast(pl.Float32),
        pl.col("Long").cast(pl.Float32),
    )
    .unique()
)

# %%
stops = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "stops.csv"))
    .select(["stop_id", "stop_lat", "stop_lon"]).with_columns(
        pl.col("stop_id").cast(pl.UInt16),
        pl.col("stop_lat").cast(pl.Float32),
        pl.col("stop_lon").cast(pl.Float32),
    )
    .unique()
)

# %%
tolerance = 0.0001 # roughly within 9m 

# %%
joined_lf = ridership.join(
    feb2020lf, how="left", left_on="Stop Id", right_on="Stop_ID"
).join(oct2022lf, how="left", left_on="IVR Number", right_on="Stop ID text")

# %%
joined_lf = joined_lf.with_columns(
    pl.when(pl.col("LAT_Num").is_not_null())
    .then(
        pl.when(
            pl.col("Lat").is_not_null()
            & ((pl.col("LAT_Num") - pl.col("Lat")).abs() <= tolerance)
        )
        .then(pl.col("LAT_Num"))
        .otherwise(pl.col("LAT_Num"))
    )
    .otherwise(pl.col("Lat"))
    .alias("Latitude"),
    pl.when(pl.col("LON_Num").is_not_null())
    .then(
        pl.when(
            pl.col("Long").is_not_null()
            & ((pl.col("LON_Num") - pl.col("Long")).abs() <= tolerance)
        )
        .then(pl.col("LON_Num"))
        .otherwise(pl.col("LON_Num"))
    )
    .otherwise(pl.col("Long"))
    .alias("Longitude"),
).select(["Stop Id", "IVR Number", "Latitude", "Longitude"])

# %%
joined_lf = joined_lf.join(stops, how="left", left_on="Stop Id", right_on="stop_id")

# %%
joined_lf = joined_lf.with_columns(
    pl.when(pl.col("Latitude").is_not_null())
    .then(
        pl.when(
            pl.col("stop_lat").is_not_null()
            & ((pl.col("Latitude") - pl.col("stop_lat")).abs() <= tolerance)
        )
        .then(pl.col("Latitude"))
        .otherwise(pl.col("Latitude"))
    )
    .otherwise(pl.col("stop_lat"))
    .alias("Latitude"),
    pl.when(pl.col("Longitude").is_not_null())
    .then(
        pl.when(
            pl.col("stop_lon").is_not_null()
            & ((pl.col("Longitude") - pl.col("stop_lon")).abs() <= tolerance)
        )
        .then(pl.col("Longitude"))
        .otherwise(pl.col("Longitude"))
    )
    .otherwise(pl.col("stop_lon"))
    .alias("Longitude"),
).select(["Stop Id", "Latitude", "Longitude"])

# %%
joined_lf.collect(streaming=True).write_csv(
    os.path.join(STAGING_DATA_FOLDER, "stops.csv")
)


