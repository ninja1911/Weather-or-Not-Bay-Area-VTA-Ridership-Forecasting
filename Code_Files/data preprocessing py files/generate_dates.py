# %%
import pandas as pd
import os

# %%
STAGING_DATA_FOLDER = "staging_data"

# %%
start_date = pd.to_datetime("2014-01-01")
end_date = pd.to_datetime("2017-12-31")

# %%
date_index = pd.date_range(start_date, end_date, freq="d")
dates = []

for i in range(len(date_index)):
    dates.append(
        {
            "id": int(
                f"{date_index[i].year}{str(date_index[i].month).zfill(2)}{str(date_index[i].day).zfill(2)}"
            )
        }
    )

# %%
pd.DataFrame(dates).to_csv(os.path.join(STAGING_DATA_FOLDER, "dates.csv"), index=False)


