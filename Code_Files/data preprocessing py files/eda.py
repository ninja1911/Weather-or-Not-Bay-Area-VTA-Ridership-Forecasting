# %%
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import polars as pl
import os

# %%
CLEAN_DATA_FOLDER = "clean_data"

# %%
ridership = pl.scan_csv(os.path.join(CLEAN_DATA_FOLDER, "ridership.csv"))

# %%
_, ax = plt.subplots(1, 1, figsize=(24, 20))
_ = sns.heatmap(
    ridership.collect().corr(),
    vmin=-1,
    vmax=1,
    annot=True,
    center=0,
    square=True,
    xticklabels=ridership.columns,
    yticklabels=ridership.columns,
    ax=ax,
)

# %%
ridership.describe()

# %%
def get_weekday(year, ordinal_day):
    date = datetime(year, 1, 1) + timedelta(days=ordinal_day - 1)
    return date.weekday()

def get_dayname(year, ordinal_day):
    date = datetime(year, 1, 1) + timedelta(days=ordinal_day - 1)
    return date.strftime("%A")

# %%
ridership = ridership.with_columns(
    pl.struct(["Year", "Day"])
    .map_elements(lambda x: get_weekday(x["Year"], x["Day"]))
    .alias("Weekday"),
    pl.struct(["Year", "Day"])
    .map_elements(lambda x: get_dayname(x["Year"], x["Day"]))
    .alias("Dayname"),
)

# %%
weekly_results = (
    ridership.group_by(["Weekday", "Dayname"])
    .agg([pl.col("On").sum(), pl.col("Off").sum()])
    .sort("Weekday")
    .select(["Dayname", "On", "Off"])
    .with_columns(pl.col("Dayname").alias("Weekday"))
    .collect()
    .to_pandas()
)

# %%
_, ax = plt.subplots(1, 1, figsize=(8, 6))
_ = sns.barplot(weekly_results, x="Weekday", y="On", ax=ax, label="On")

# %%
yearly_day_counts = (
    ridership.select(["Year", "Day", "On", "Off"])
    .group_by(["Year", "Day"])
    .agg([pl.col("On").sum(), pl.col("Off").sum()])
    .sort(["Year", "Day"])
    .collect()
    .to_pandas()
)

# %%
yearly_day_counts.head()

# %%
_, ax = plt.subplots(1, 1, figsize=(16, 12))
_ = sns.lineplot(yearly_day_counts, x="Day", y="On", hue="Year", palette=sns.color_palette("tab10", 4), linewidth=1, ax=ax)

# %%
_, ax = plt.subplots(2, 2, figsize=(21, 21))
ax[0][0].set_ylim(55, 180640)
_ = sns.lineplot(
    yearly_day_counts[yearly_day_counts["Year"] == 2014],
    x="Day",
    y="On",
    hue="Year",
    palette=sns.color_palette("tab10"),
    ax=ax[0][0],
)
ax[0][1].set_ylim(55, 180640)
_ = sns.lineplot(
    yearly_day_counts[yearly_day_counts["Year"] == 2015],
    x="Day",
    y="On",
    hue="Year",
    palette=sns.color_palette("tab10"),
    ax=ax[0][1],
)
ax[1][0].set_ylim(55, 180640)
_ = sns.lineplot(
    yearly_day_counts[yearly_day_counts["Year"] == 2016],
    x="Day",
    y="On",
    hue="Year",
    palette=sns.color_palette("tab10"),
    ax=ax[1][0],
)
ax[1][1].set_ylim(55, 180640)
_ = sns.lineplot(
    yearly_day_counts[yearly_day_counts["Year"] == 2017],
    x="Day",
    y="On",
    hue="Year",
    palette=sns.color_palette("tab10"),
    ax=ax[1][1],
)


