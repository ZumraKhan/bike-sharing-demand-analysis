"""
Load and clean the UCI Bike Sharing dataset.

Source : Fanaee-T, H. & Gama, J. (2013), Capital Bikeshare (Washington D.C.),
         hourly and daily logs for 2011-2012.
The raw file ships with min-max normalised weather columns; this module
restores them to physical units so that every chart and table in the project
is readable in degrees Celsius, % and km/h.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# Label maps taken from the dataset's own Readme.txt
SEASONS = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHER = {1: "Clear / Few clouds",
           2: "Mist / Cloudy",
           3: "Light snow or rain",
           4: "Heavy rain / snow"}
WEEKDAYS = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}
MONTHS = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
          7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

# De-normalisation constants documented in Readme.txt
TEMP_MAX, ATEMP_MAX, HUM_MAX, WIND_MAX = 41.0, 50.0, 100.0, 67.0


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["dteday"] = pd.to_datetime(df["dteday"])

    # Restore physical units
    df["temp_c"] = df["temp"] * TEMP_MAX
    df["atemp_c"] = df["atemp"] * ATEMP_MAX
    df["humidity"] = df["hum"] * HUM_MAX
    df["wind_kmh"] = df["windspeed"] * WIND_MAX

    # Readable labels
    df["year"] = df["yr"].map({0: 2011, 1: 2012})
    df["season_name"] = df["season"].map(SEASONS)
    df["weather_name"] = df["weathersit"].map(WEATHER)
    df["weekday_name"] = df["weekday"].map(WEEKDAYS)
    df["month_name"] = df["mnth"].map(MONTHS)
    df["day_type"] = df["workingday"].map({1: "Working day", 0: "Weekend / holiday"})

    # Share of demand coming from unregistered riders
    df["casual_share"] = (df["casual"] / df["cnt"].replace(0, pd.NA)) * 100
    return df


def load_hourly() -> pd.DataFrame:
    df = pd.read_csv(RAW / "hour.csv")
    df = _enrich(df)
    df["timestamp"] = df["dteday"] + pd.to_timedelta(df["hr"], unit="h")
    return df.sort_values("timestamp").reset_index(drop=True)


def load_daily() -> pd.DataFrame:
    return _enrich(pd.read_csv(RAW / "day.csv")).sort_values("dteday").reset_index(drop=True)


def quality_report(hourly: pd.DataFrame, daily: pd.DataFrame) -> dict:
    """Facts used by the data-quality section of the report."""
    full_range = pd.date_range(hourly["timestamp"].min(),
                               hourly["timestamp"].max(), freq="h")
    missing_hours = len(full_range) - hourly["timestamp"].nunique()
    return {
        "hourly_rows": int(len(hourly)),
        "daily_rows": int(len(daily)),
        "columns": int(hourly.shape[1]),
        "date_start": str(hourly["dteday"].min().date()),
        "date_end": str(hourly["dteday"].max().date()),
        "missing_values": int(hourly.isna().drop(columns=["casual_share"],
                                                 errors="ignore").sum().sum()),
        "duplicate_rows": int(hourly.duplicated().sum()),
        "duplicate_timestamps": int(hourly["timestamp"].duplicated().sum()),
        "expected_hours": int(len(full_range)),
        "missing_hours": int(missing_hours),
        "coverage_pct": round(100 * hourly["timestamp"].nunique() / len(full_range), 2),
        "cnt_equals_casual_plus_registered": bool(
            (hourly["cnt"] == hourly["casual"] + hourly["registered"]).all()),
        "zero_demand_hours": int((hourly["cnt"] == 0).sum()),
    }
