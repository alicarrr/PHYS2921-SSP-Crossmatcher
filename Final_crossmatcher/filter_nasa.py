import pandas as pd
import matplotlib.pyplot as plt
# archive = pd.read_csv("NASA_exoplanet_archive_with_proper_motion.csv",sep=',',header=47,low_memory=False)

def filter_nasa_database(archive: pd.DataFrame, dec_lower_limit: float, orbital_period_lower: float, jp_mass_upper_limit: float, dist_to_earth_upper: float):
    nasa_filtered_no_na = archive.dropna(subset=["dec"])
    nasa_filtered = nasa_filtered_no_na[(nasa_filtered_no_na["dec"] > dec_lower_limit) & (nasa_filtered_no_na["pl_orbper"] < orbital_period_lower) & (nasa_filtered_no_na["pl_massj"] > jp_mass_upper_limit) & (nasa_filtered_no_na['sy_dist'] < dist_to_earth_upper) ]

    # Convert filtered planets to csv
    nasa_filtered.to_csv("nasa_filtered.csv", index = False)

    # Print number of planets found
    print(f"Number of planets in database matching all criteria: {len(nasa_filtered)}")

# filter_nasa_database(archive, 40, 7, 1, 100)