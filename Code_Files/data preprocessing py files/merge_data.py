# %%
import polars as pl
import os

# %%
STAGING_DATA_FOLDER = "staging_data"
CLEAN_DATA_FOLDER = "clean_data"

# %%
ridership = pl.scan_csv(os.path.join(STAGING_DATA_FOLDER, "ridership.csv"))
climate = pl.scan_csv(os.path.join(STAGING_DATA_FOLDER, "climate.csv"))
stops = pl.scan_csv(os.path.join(STAGING_DATA_FOLDER, "stops.csv"))
dates = (
    pl.scan_csv(os.path.join(STAGING_DATA_FOLDER, "dates.csv"))
    .with_columns(
        pl.col("id")
        .cast(pl.Utf8)
        .str.strptime(pl.Date, "%Y%m%d")
        .cast(pl.String)
        .alias("Date")
    )
    .select(["Date"])
)

# %%
stops_with_dates = dates.join(stops, how="cross")

# %%
def distance(lat1, long1, lat2, long2):
    return ((lat1 - lat2) ** 2 + (long1 - long2) ** 2) ** 0.5

# %%
stops_with_dates_and_climate = (
    stops_with_dates.join(climate, on="Date", suffix="_station")
    .with_columns(
        [
            distance(
                pl.col("Latitude"),
                pl.col("Longitude"),
                pl.col("Latitude_station"),
                pl.col("Longitude_station"),
            ).alias("Distance")
        ]
    )
    .sort(["Stop Id", "Date", "Latitude", "Longitude", "Distance"])
    .group_by(["Stop Id", "Date", "Latitude", "Longitude"], maintain_order=True)
    .first()
    .select(["Stop Id", "Date", "Latitude", "Longitude", "Tmax", "Tmin", "Prcp"])
)

# %%
ridership = (
    ridership.join(stops_with_dates_and_climate, on=["Date", "Stop Id"], how="left")
    .with_columns(pl.col("Date").cast(pl.Date))
    .with_columns(
        pl.col("Date").dt.year().alias("Year"),
        pl.col("Date").dt.ordinal_day().alias("Day"),
    )
    .drop("Date")
    .select(
        [
            "Year",
            "Day",
            "Line",
            "Service",
            "Direction Number",
            "Sequence",
            "Latitude",
            "Longitude",
            "Tmax",
            "Tmin",
            "Prcp",
            "On",
            "Off",
        ]
    )
)

# %%
ridership.collect(streaming=True).write_csv(
    os.path.join(CLEAN_DATA_FOLDER, "ridership.csv")
)


