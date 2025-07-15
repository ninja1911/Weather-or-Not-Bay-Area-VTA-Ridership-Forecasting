# %%
from datetime import timedelta
import polars as pl
import os

# %%
RAW_DATA_FOLDER = "raw_data"
STAGING_DATA_FOLDER = "staging_data"

# %%
ridership = pl.scan_csv(os.path.join(RAW_DATA_FOLDER, "Ridership.csv")).select(
    [
        "Date",
        "Line",
        "Service",
        "Direction Number",
        "From Time",
        "On",
        "Off",
        "Stop Id",
        "Sequence",
    ]
)

# %%
ridership = ridership.with_columns(
    pl.col("Date").str.strptime(pl.Datetime, "%m/%d/%Y %I:%M:%S %p").dt.date(),
    pl.col("Line").cast(pl.UInt16),
    pl.col("Service").cast(pl.UInt8),
    pl.col("Direction Number").cast(pl.UInt8),
    pl.col("From Time").cast(pl.UInt32),
    pl.col("On").cast(pl.Int16),
    pl.col("Off").cast(pl.Int16),
    pl.col("Stop Id").str.replace_all(",", "").cast(pl.UInt16),
    pl.col("Sequence").cast(pl.UInt8),
)
ridership = ridership.select(
    [
        "Date",
        "Line",
        "Service",
        "Direction Number",
        "From Time",
        "Stop Id",
        "Sequence",
        "On",
        "Off",
    ]
)

# %%
ridership = ridership.filter(pl.col("On") >= 0)

# %%
# ridership = ridership.with_columns(
#     pl.when(pl.col("From Time") > 86400)
#     .then(pl.col("Date") + timedelta(days=1))
#     .otherwise(pl.col("Date"))
#     .alias("Date"),
#     pl.when(pl.col("From Time") > 86400)
#     .then(pl.col("From Time") - 86400)
#     .otherwise(pl.col("From Time"))
#     .alias("From Time"),
# )

# %%
# ridership = ridership.filter(pl.col("Date").dt.year() < 2018)

# %%
# ridership = ridership.with_columns(
#     pl.when(pl.col("Direction").is_in(["NORTH", "SOUTH"]))
#     .then(1)
#     .when(pl.col("Direction").is_in(["EAST", "WEST"]))
#     .then(2)
#     .when(pl.col("Direction").is_in(["NORTHBOUND", "SOUTHBOUND"]))
#     .then(3)
#     .when(pl.col("Direction").is_in(["LOOP", "REVERSE"]))
#     .then(4)
#     .otherwise(0)
#     .alias("Direction")
# )

# %%
ridership = ridership.group_by(
    [
        "Line",
        "Service",
        "Direction Number",
        "Sequence",
        "Stop Id",
        "Date",
    ]
).agg([pl.col("On").sum().alias("On"), pl.col("Off").sum().alias("Off")])

# %%
ridership.collect(streaming=True).write_csv(
    os.path.join(STAGING_DATA_FOLDER, "ridership.csv")
)


