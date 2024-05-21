import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord, Distance
import astropy.units as un
from astropy.time import Time, TimeDelta
from astropy.coordinates import Angle, Latitude, Longitude

# Intialise logger 
from logger_config import logger  # Import the centralized logger

def filter_for_gaia(source_list_sorted):
    # Dropping rows from source_list_sorted with missing `gaia_id`
    source_list_sorted = source_list_sorted.dropna(subset=['gaia_id'])

    # Filtering out planet systems that don't have Gaia DR2 numbers, so that the same J2015.5 reference epoch can be used for all proper motion corrections below. 
    source_list_filtered = source_list_sorted.loc[source_list_sorted["gaia_id"].str.contains('Gaia DR2')]

    # Dropping rows from source_list_filtered with missing 'sy_refname' (system parameter reference). 
    source_list_sorted_2 = source_list_filtered.dropna(subset=['sy_refname'])

    #Filtering out planet systems that don't have TICv8 (TESS Input Catalogue revised for Gaia DR2) system parameter reference numbers, so that J2015.5 reference epoch can be used. 
    source_list_filtered_2 = source_list_sorted_2.loc[source_list_sorted_2['sy_refname'].str.contains('TICv8')]

    return source_list_filtered_2

    
def proper_correct_planet(hot_jupiter_source_df: pd.DataFrame, planet_name_to_correct: str):
    """
    Use "*_Sourcelist_3.csv" for 10 planet sample 
    Use "*_Sourcelist_4.csv" for 88 planet sample
    Use "NASA_exoplanet_archive_declination_filtered_with_proper_motion_values.csv" for full archive filtered for +40 declination
    """

    # Check if source_list was successfully assigned
    if hot_jupiter_source_df is not None:
        # Filter rows based on pl_name
        filtered_rows = hot_jupiter_source_df[hot_jupiter_source_df['pl_name'] == planet_name_to_correct]

        if len(filtered_rows) == 0:
            logger.info(f"No rows found with pl_name '{planet_name_to_correct}'. No correction applied.")
            return hot_jupiter_source_df

        RA = filtered_rows["ra"].to_numpy()
        DEC = filtered_rows["dec"].to_numpy()
        PMRA = filtered_rows["sy_pmra"].to_numpy()
        PMDEC = filtered_rows["sy_pmdec"].to_numpy()
        DISTANCE = filtered_rows["sy_dist"].to_numpy()
        OBSTIME = Time('J2015.5')
        epoch = filtered_rows['epoch']

        initial_coords = SkyCoord(RA * un.deg, DEC * un.deg,
                                  pm_ra_cosdec=PMRA * un.mas / un.yr,
                                  pm_dec=PMDEC * un.mas / un.yr,
                                  frame='icrs', obstime=OBSTIME,
                                  distance=DISTANCE * un.pc)
        
        propermotion_coords = initial_coords.apply_space_motion(Time(epoch, format='mjd'))

        # Update the original DataFrame with corrected coordinates
        hot_jupiter_source_df.loc[hot_jupiter_source_df['pl_name'] == planet_name_to_correct, 'ra_corrected'] = propermotion_coords.ra.deg
        hot_jupiter_source_df.loc[hot_jupiter_source_df['pl_name'] == planet_name_to_correct, 'dec_corrected'] = propermotion_coords.dec.deg

        return hot_jupiter_source_df
    else:
        logger.info("Source list could not be initialized.")
        return None