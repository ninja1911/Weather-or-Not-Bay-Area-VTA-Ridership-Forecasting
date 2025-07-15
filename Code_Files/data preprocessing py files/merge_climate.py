# %% [markdown]
# ```python
# >>> df["Latitude"].min()
# 36.974922
# >>> df["Latitude"].max()
# 37.558388
# >>> df["Longitude"].min()
# -122.17364
# >>> df["Longitude"].max()
# -121.54903
# ```

# %%
import polars as pl
import os

# %%
RAW_DATA_FOLDER = "raw_data"
STAGING_DATA_FOLDER = "staging_data"
ELEMENTS = ["TMAX", "TMIN", "PRCP"]

# %%
stations = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "stations.csv"))
    .select(["id", "latitude", "longitude"])
    .with_columns(
        pl.col("latitude").cast(pl.Float32), pl.col("longitude").cast(pl.Float32)
    )
    .filter((pl.col("latitude").ge(36.97)) & (pl.col("latitude").le(37.56)))
    .filter((pl.col("longitude").ge(-122.18)) & (pl.col("longitude").le(-121.54)))
)

# %%
climate = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "2014.csv"))
    .select([pl.col("ID"), pl.col("DATE"), pl.col("ELEMENT"), pl.col("DATA_VALUE")])
    .with_columns(pl.col("DATE").cast(pl.Utf8).str.strptime(pl.Date, "%Y%m%d"))
    .with_columns((pl.col("DATA_VALUE") / 10).cast(pl.Float32))
    .filter(pl.col("ELEMENT").is_in(ELEMENTS))
    .filter(pl.col("ID").is_in(stations.select("id").collect()))
    .unique(["ID", "DATE", "ELEMENT"])
    .group_by(["ID", "DATE"])
    .agg(
        pl.col("DATA_VALUE")
        .filter(pl.col("ELEMENT").eq(element))
        .alias(element)
        .mean()
        for element in ELEMENTS
    )
)

# %%
lf = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "2015.csv"))
    .select([pl.col("ID"), pl.col("DATE"), pl.col("ELEMENT"), pl.col("DATA_VALUE")])
    .with_columns(pl.col("DATE").cast(pl.Utf8).str.strptime(pl.Date, "%Y%m%d"))
    .with_columns((pl.col("DATA_VALUE") / 10).cast(pl.Float32))
    .filter(pl.col("ELEMENT").is_in(ELEMENTS))
    .filter(pl.col("ID").is_in(stations.select("id").collect()))
    .unique(["ID", "DATE", "ELEMENT"])
    .group_by(["ID", "DATE"])
    .agg(
        pl.col("DATA_VALUE")
        .filter(pl.col("ELEMENT").eq(element))
        .alias(element)
        .mean()
        for element in ELEMENTS
    )
)
climate = pl.concat([climate, lf], how="vertical")

# %%
lf = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "2016.csv"))
    .select([pl.col("ID"), pl.col("DATE"), pl.col("ELEMENT"), pl.col("DATA_VALUE")])
    .with_columns(pl.col("DATE").cast(pl.Utf8).str.strptime(pl.Date, "%Y%m%d"))
    .with_columns((pl.col("DATA_VALUE") / 10).cast(pl.Float32))
    .filter(pl.col("ELEMENT").is_in(ELEMENTS))
    .filter(pl.col("ID").is_in(stations.select("id").collect()))
    .unique(["ID", "DATE", "ELEMENT"])
    .group_by(["ID", "DATE"])
    .agg(
        pl.col("DATA_VALUE")
        .filter(pl.col("ELEMENT").eq(element))
        .alias(element)
        .mean()
        for element in ELEMENTS
    )
)
climate = pl.concat([climate, lf], how="vertical")

# %%
lf = (
    pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "2017.csv"))
    .select([pl.col("ID"), pl.col("DATE"), pl.col("ELEMENT"), pl.col("DATA_VALUE")])
    .with_columns(pl.col("DATE").cast(pl.Utf8).str.strptime(pl.Date, "%Y%m%d"))
    .with_columns((pl.col("DATA_VALUE") / 10).cast(pl.Float32))
    .filter(pl.col("ELEMENT").is_in(ELEMENTS))
    .filter(pl.col("ID").is_in(stations.select("id").collect()))
    .unique(["ID", "DATE", "ELEMENT"])
    .group_by(["ID", "DATE"])
    .agg(
        pl.col("DATA_VALUE")
        .filter(pl.col("ELEMENT").eq(element))
        .alias(element)
        .mean()
        for element in ELEMENTS
    )
)
climate = pl.concat([climate, lf], how="vertical")

# %%
climate95 = (
    climate.group_by("ID")
    .agg(
        [
            pl.col("DATE").len(),
            pl.col("TMAX").null_count(),
            pl.col("TMIN").null_count(),
            pl.col("PRCP").null_count(),
        ]
    )
    .filter((pl.col("PRCP") / pl.col("DATE")) < 0.05)
    .filter((pl.col("TMAX") / pl.col("DATE")) < 0.05)
    .select("ID")
    .collect()
)
climate = climate.filter(pl.col("ID").is_in(climate95))

# %%
dates = (
    pl.scan_csv(os.path.join(STAGING_DATA_FOLDER, "dates.csv"))
    .with_columns(
        pl.col("id").cast(pl.Utf8).str.strptime(pl.Date, "%Y%m%d").alias("DATE")
    )
    .select(pl.col("DATE"))
)

# %%
unique_stations = climate.select("ID").unique()
unique_stations = unique_stations.join(dates, on="DATE", how="cross")
climate = unique_stations.join(climate, on=["ID", "DATE"], how="left")

# %%
def impute_median(df, group):
    # Calculate median per group
    median_df = df.group_by(["ID", "YEAR", group]).agg(
        pl.col("TMAX").median().alias("median_TMAX"),
        pl.col("TMIN").median().alias("median_TMIN"),
        pl.col("PRCP").median().alias("median_PRCP"),
    )
    # Join back to the original data to align the medians
    df = df.join(median_df, on=["ID", "YEAR", group])
    # Impute the nulls with the corresponding median
    df = df.with_columns(
        pl.when(pl.col("TMAX").is_null())
        .then(pl.col("median_TMAX"))
        .otherwise(pl.col("TMAX"))
        .alias("TMAX"),
        pl.when(pl.col("TMIN").is_null())
        .then(pl.col("median_TMIN"))
        .otherwise(pl.col("TMIN"))
        .alias("TMIN"),
        pl.when(pl.col("PRCP").is_null())
        .then(pl.col("median_PRCP"))
        .otherwise(pl.col("PRCP"))
        .alias("PRCP"),
    )
    # Drop the median column after imputation
    df = df.drop(["median_TMAX", "median_TMIN", "median_PRCP"])
    return df

# %%
climate = climate.with_columns(
    pl.col("DATE").dt.year().alias("YEAR"),
    pl.col("DATE").dt.week().alias("WEEK"),
    pl.col("DATE").dt.month().alias("MONTH"),
    pl.col("DATE").dt.quarter().alias("QUARTER"),
)
# climate = climate.pipe(impute_median, "WEEK")
climate = climate.pipe(impute_median, "MONTH")
# climate = climate.pipe(impute_median, "QUARTER")
climate = climate.drop(["YEAR", "WEEK", "MONTH", "QUARTER"])

# %%
climate = climate.with_columns(
    pl.col("TMAX").fill_null(pl.col("TMAX").median()),
    pl.col("TMIN").fill_null(pl.col("TMIN").median()),
    pl.col("PRCP").fill_null(0.0),
)

# %%
climate = climate.join(stations, how="left", left_on="ID", right_on="id").select(
    [
        pl.col("DATE").alias("Date"),
        pl.col("latitude").alias("Latitude"),
        pl.col("longitude").alias("Longitude"),
        pl.col("TMAX").alias("Tmax"),
        pl.col("TMIN").alias("Tmin"),
        pl.col("PRCP").alias("Prcp"),
    ]
)

# %%
climate.collect(streaming=True).write_csv(
    os.path.join(STAGING_DATA_FOLDER, "climate.csv")
)


