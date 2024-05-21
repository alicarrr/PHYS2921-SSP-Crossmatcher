import numpy as np
import pandas as pd
import os, re
from datetime import datetime
from astropy.table import Table
from astroquery.casda import Casda
from astroquery.utils.tap.core import TapPlus
from astropy.io.votable import parse
from astropy.coordinates import SkyCoord
import astropy.units as un

# Import the centralized logger
from logger_config import logger


def convert_xml_to_pandas(xml_file_name: str):
    """Convert an xml file to a pandas dataframe

    Args:
        xml_file_name (str): Name of XML File to be converted

    Returns:
        DataFrame: xml file as a pandas DataFrame
    """
    votable = parse(xml_file_name)
    table = votable.get_first_table()
    bill = table.to_table(use_names_over_ids=True)
    return bill.to_pandas()


def check_casda_cache() -> bool:
    '''
    Checks if pubdat cache (casda_cache\\pubdat-YYYY-MM-DD.csv) already exists        
    '''
    # match pubdat-YYYY-MM-DD.csv
    pattern = r"pubdat-\d{4}-\d{2}-\d{2}\.csv"

    # absolute path to casda cache folder ("Final_crossmatcher\\casda_cache")
    directory = os.path.join(os.path.dirname(__file__), "casda_cache\\")

    if not os.path.exists(directory):
        return False
    
    # List all files in the directory
    files = os.listdir(directory)

    # Filter files matching the pattern
    for file in files:
        if re.match(pattern, file):
            return True
    return False

def pandas_to_csv(output_filename: str, download_path: str, dataframe: pd.DataFrame) -> None:
    """Converts a pandas DataFrame into a csv and saves it in the requested directory

    Args:
        output_filename (str): Name of csv output file
        download_path (str): directory to save csv file to
        dataframe (pd.DataFrame): DataFrame to be converted to a csv file

    """

    # Name of csv output file
    csv_output_name = output_filename + '.csv' 

    # creates directory if it doesnt exist
    os.makedirs(download_path, exist_ok = True)

    # Save csv file in the location specified as 'download_path'
    output_path = os.path.join(download_path, csv_output_name)
    dataframe.to_csv(output_path, index=False) # NOTE: index=False tells panda to not create row index column


def delete_directory_contents(directory_path: str) -> None:
    """Helper file to clear files in cache folder

    Args:
        directory_path (str): Directory of files to be cleared
    """

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        # Filepath of file
        filepath = os.path.join(directory_path, filename)
        try:
            # Delete file from directory if it is a file not the directory itself
            if os.path.isfile(filepath):
                os.unlink(filepath)
            elif os.path.isdir(filepath):
                os.rmdir(filepath)
        except Exception as e:
            logger.error(f"Failed to delete {filepath} from cache. Reason: {e}")


def get_public_data_table(refresh:bool=False) -> Table:
    '''
    Retrieve top CATALOGUE_COUNT of continuum catalogues from CASDA
        
    Args:
        refresh (bool): search radius in ARCSECONDS 

    Returns:
        Top CATALOGUE_COUNT continuum catalogues as a pandas dataframe
    '''
    CATALOGUE_COUNT = 50000 # 50000 default
    # CACHE_FOLDER = os.path.join(os.path.dirname(__file__), "casda_cache\\")

    CACHE_FOLDER = os.path.join(os.path.dirname(__file__), "casda_cache\\")
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER, exist_ok=True)

    # check cache if refresh=False
    if check_casda_cache() and not refresh:
        cache_filenames = os.listdir(CACHE_FOLDER)
        cache_path = CACHE_FOLDER + cache_filenames[0]

        return pd.read_csv(cache_path)

    # clear cache
    delete_directory_contents(CACHE_FOLDER)

    # Set up the TAP url
    tap = TapPlus(url="https://casda.csiro.au/casda_vo_tools/tap")

    # Search for continuum catalogues
    job = tap.launch_job_async((f"SELECT TOP {CATALOGUE_COUNT} * FROM ivoa.obscore where(dataproduct_subtype = 'catalogue.continuum.component')"))
    # return the results 
    r = job.get_results()

    # Keep only good or uncertain data
    data = r[(r['quality_level'] == 'GOOD') | (r['quality_level'] == 'UNCERTAIN')]

    # You have to do this step unless you have permission for embargoed data 
    # associated with you OPAL account login
    public_data_df = Casda.filter_out_unreleased(data).to_pandas() # astropy table

    # save pubdata as cache
    cache_filename = "pubdat-" + datetime.now().strftime("%Y-%m-%d")
    cache_path = CACHE_FOLDER + cache_filename + ".csv"
    cache_filenames_path = CACHE_FOLDER + cache_filename + ".txt"
    public_data_df.to_csv(cache_path, index=False)
    public_data_df['filename'].to_csv(cache_filenames_path)
    
    return public_data_df


def casda_search_closest_catalogue(source_ra: float, source_dec: float, casda: Casda = None, 
                                   refresh:bool=False, debug:bool=False) -> str:
    """
    Finds catalogue file corresponding to closest match to source

    Args:
        source_ra (float): source right ascension
        source_dec (float): source declination
        casda (Casda): casda instance
        debug (bool) = False : print debug information
    Returns:
        closest_catalogue_filename (str): filename of the closest source match catalogue
    """
    
    CASDA_XML_DOWNLOAD_PATH = os.path.join(os.path.dirname(__file__), "casda_xml_downloads\\")
    TARGET_SOURCE_COORDS    = SkyCoord(ra = source_ra * un.deg, dec = source_dec * un.deg)
    CATALOGUE_SEARCH_RADIUS = 3 * un.deg # based on CASDA uncertainty

    if debug:
        logger.info(f"Target source {TARGET_SOURCE_COORDS}")

    '''
    CASDA login and setup
    '''
    # Your OPAL username for login
    if casda == None:
        username = input('Enter your CASDA username (email): ')
        casda = Casda()
        casda.login(username=username)

    '''
    Retrieving and filtering casda continuum catalogues (xml files)
    '''
    # get CASDA continuum catalogues
    # A choice was made here to only consider .cont.taylor.0.restored.conv.components.xml files to restrict data
    if debug:
        logger.info("Beginning pubdat retrieval")

    pattern = r'.*.cont.taylor.0.restored.conv.components.xml$'
    pubdat = get_public_data_table(refresh=refresh)
    reduced_pubdat = pubdat[pubdat['filename'].str.contains(pattern, regex=True)]

    if debug:
        logger.info(f"pubdat files retrieved: \n {pubdat['filename']}")
        logger.info(f"reduced pubdat files retrieved: \n {reduced_pubdat['filename']}")
    
    # Get the centre coordsof all of the continuum catalogues in the table
    center_coords = SkyCoord(np.array(reduced_pubdat['s_ra']) * un.deg, 
                             np.array(reduced_pubdat['s_dec']) * un.deg)
    # find which files in pubdat have center coordinates within catalogue_search_radius of source
    seps = TARGET_SOURCE_COORDS.separation(center_coords).to('arcsecond') 
    matches = np.where(seps < CATALOGUE_SEARCH_RADIUS.to('arcsecond') )[0]
    matching_files = np.array(reduced_pubdat.iloc[matches]['filename'])

    if debug:
        logger.info(f"matching indices: {matches}")
        logger.info("matching separations between target source and catalogue center coordinates in deg:")
        for i in matches:
            # Access separation, center coordinate, and matching filename
            sep_deg = seps[i].degree
            center_coord = center_coords[i]
            filename = reduced_pubdat.iloc[i]['filename']
            
            # Print information
            logger.info(f"({i:02d}): sep (deg): {sep_deg:<20}, from catalogue center (ra, dec) in deg: ({center_coord.ra.value}, {center_coord.dec.value}); Matching filename: {filename}")

        logger.info(f"matching_files: \n {matching_files}")
        logger.info("Starting file download staging")

    # This part stages the files you want to download so it sometimes takes a minute
    url_list = []
    for mfile in matching_files:
        pdata = reduced_pubdat[reduced_pubdat['filename'] == mfile]
        ptable = Table.from_pandas(pdata)
        urls = casda.stage_data(ptable, verbose=debug)
        for url in urls:
            if url not in url_list:
                url_list.append(url)

    # filter through checksum files
    url_list = list(filter(lambda url: 'checksum' not in url, url_list))

    if debug:
        logger.info(f"url_list: \n {url_list}")
        logger.info("Begin XML file download:")

    # ensure xml download directory exists
    if not os.path.exists(CASDA_XML_DOWNLOAD_PATH):
        os.makedirs(CASDA_XML_DOWNLOAD_PATH)

    # file download
    try:
        xml_filelist = casda.download_files(url_list, savedir=CASDA_XML_DOWNLOAD_PATH)
    except Exception as e:
        logger.error(e)
        return None 

    '''
    Searching for planet through xml dataset
    '''
    catalogue_dfs = pd.DataFrame()
    for xml_file in xml_filelist:
        catalogue_df = convert_xml_to_pandas(xml_file)
        try:
            filename = xml_file.split("\\")[-1]
        except IndexError:
            filename = ""
        catalogue_df['source_filename'] = filename
        catalogue_dfs = pd.concat([catalogue_dfs, catalogue_df], ignore_index=True)

    if not url_list:
        return None

    catalogue_dfs = catalogue_dfs.sort_values(by=['ra_deg_cont', 'dec_deg_cont'])

    if debug:
        logger.info(f"catalogue_dfs: \n {catalogue_dfs}")
        
    catalogue_coords = SkyCoord(ra = np.array(catalogue_dfs['ra_deg_cont']) * un.deg,
                                dec = np.array(catalogue_dfs['dec_deg_cont']) * un.deg)
    
    seps = TARGET_SOURCE_COORDS.separation(catalogue_coords).to('arcsecond') 

    # return closest match
    closest_catalogue_filename = None
    sorted_indices = seps.argsort()

    first_index = sorted_indices[0]
    closest_catalogue_filename = catalogue_dfs['source_filename'][first_index]

    if debug:
        logger.info(f"closest source match catalogue: {closest_catalogue_filename}")
    
    return closest_catalogue_filename


def extract_epoch_from_pubdat_catalogue(filename: str) -> float:
    """_summary_

    Args:
        filename (str): name of file in the pubdat archive to be used as an epoch. 

    Returns:
        epoch (float): time of matching file from pubdat to be used for proper motion correction 
    or returns None
    """
    CACHE_FOLDER = os.path.join(os.path.dirname(__file__), "casda_cache\\")
    pubdat_csv_filepath = None

    for cache_filename in os.listdir(CACHE_FOLDER):
        if ".csv" in cache_filename:
            pubdat_csv_filepath = cache_filename
            break

    if pubdat_csv_filepath:
        pubdat_df = pd.read_csv(CACHE_FOLDER + "\\" + pubdat_csv_filepath)
        filtered_rows = pubdat_df[pubdat_df['filename'] == filename]
        t_max_values = filtered_rows['t_max']
        epoch = t_max_values.values[0]
        return epoch
    
    return None
    

def casda_search(source_ra: float, source_dec: float, search_radius: float =3, output_filename: str='matches',
                 casda = None, refresh=False, debug=False) -> pd.DataFrame:
    """
    Generate csv of matches of given source with CASDA continuum catalogues

    Args:
        source_ra (float): source right ascension
        source_dec (float): source declination
        search_radius (float): search radius in ARCSECONDS
        casda (Casda): casda instance
        # output_filename (str): filename of output csv [i.e. <output_filename>.csv]
        # debug (booolean) = False : print debug information
    """
    
    CASDA_CSV_DOWNLOAD_PATH = os.path.join(os.path.dirname(__file__), "casda_csv_downloads\\")
    CASDA_XML_DOWNLOAD_PATH = os.path.join(os.path.dirname(__file__), "casda_xml_downloads\\")
    CASDA_MATCHES_PATH      = os.path.join(os.path.dirname(__file__), "casda_matches\\")
    TARGET_SOURCE_COORDS    = SkyCoord(ra = source_ra * un.deg, dec = source_dec * un.deg)
    CATALOGUE_SEARCH_RADIUS = 3 * un.deg # based on CASDA uncertainty
    SEARCH_RADIUS           = search_radius * un.arcsecond

    # colored text
    TYELLOW = "\033[1;33m"
    TRESET = "\033[m"

    if debug:
        logger.info(f"Target source {TARGET_SOURCE_COORDS}")

    '''
    CASDA login and setup
    '''
    # Your OPAL username for login
    if casda == None:
        username = input('Enter your CASDA username (email): ')
        casda = Casda()
        casda.login(username=username)

    '''
    Retrieving and filtering casda continuum catalogues (xml files)
    '''
    # get CASDA continuum catalogues
    # A choice was made here to only consider .cont.taylor.0.restored.conv.components.xml files to restrict data
    if debug:
        logger.info("Beginning pubdat retrieval")

    pattern = r'.*.cont.taylor.0.restored.conv.components.xml$'
    pubdat = get_public_data_table(refresh=refresh)
    reduced_pubdat = pubdat[pubdat['filename'].str.contains(pattern, regex=True)]

    if debug:
        logger.info(f"pubdat files retrieved: \n {pubdat['filename']}")
        logger.info(f"reduced pubdat files retrieved: \n {reduced_pubdat['filename']}")
    
    # Get the centre coordsof all of the continuum catalogues in the table
    center_coords = SkyCoord(np.array(reduced_pubdat['s_ra'])*un.deg, 
                             np.array(reduced_pubdat['s_dec'])*un.deg)
    # find which files in pubdat have center coordinates within catalogue_search_radius of source
    seps = TARGET_SOURCE_COORDS.separation(center_coords).to('arcsecond') 
    matches = np.where(seps < CATALOGUE_SEARCH_RADIUS.to('arcsecond') )[0]
    matching_files = np.array(reduced_pubdat.iloc[matches]['filename'])


    if debug:
        logger.info(f"matching indices: {matches}")
        logger.info("matching separations between target source and catalogue center coordinates in deg:")
        for i in matches:
            # Access separation, center coordinate, and matching filename
            sep_deg = seps[i].degree
            center_coord = center_coords[i]
            filename = reduced_pubdat.iloc[i]['filename']
            
            # Print information
            logger.info(f"({i:02d}): sep (deg): {sep_deg:<20}, from catalogue center (ra, dec) in deg: ({center_coord.ra.value}, {center_coord.dec.value}); Matching filename: {filename}")

        logger.info(f"matching_files: \n {matching_files}")
        logger.info("Starting file download staging")

    # This part stages the files you want to download so it sometimes takes a minute
    url_list = []
    for mfile in matching_files:
        pdata = reduced_pubdat[reduced_pubdat['filename'] == mfile]
        ptable = Table.from_pandas(pdata)
        urls = casda.stage_data(ptable, verbose=debug)
        for url in urls:
            if url not in url_list:
                url_list.append(url)

    # filter through checksum files
    url_list = list(filter(lambda url: 'checksum' not in url, url_list))

    if debug:
        logger.info(f"url_list: \n {url_list}")

    # ensure xml download directory exists
    if not os.path.exists(CASDA_XML_DOWNLOAD_PATH):
        os.makedirs(CASDA_XML_DOWNLOAD_PATH)
    
    if debug:
        logger.info("Begin XML file download:")

    # file download
    try:
        xml_filelist = casda.download_files(url_list, savedir=CASDA_XML_DOWNLOAD_PATH)
    except Exception as e:
        logger.error(e)
        return None
    
    '''
    Searching for planet through xml dataset
    '''
    catalogue_dfs = pd.DataFrame()
    for xml_file in xml_filelist:
        catalogue_df = convert_xml_to_pandas(xml_file)
        try:
            filename = xml_file.split("\\")[-1]
        except IndexError:
            filename = ""
        catalogue_df['source_filename'] = filename
        catalogue_dfs = pd.concat([catalogue_dfs, catalogue_df], ignore_index=True)

    # ensure csv download directory exists
    if not os.path.exists(CASDA_CSV_DOWNLOAD_PATH):
        os.makedirs(CASDA_CSV_DOWNLOAD_PATH)

    if not url_list:
        return None
    
    catalogue_dfs = catalogue_dfs.sort_values(by=['ra_deg_cont', 'dec_deg_cont'])

    catalogue_dfs.to_csv(CASDA_CSV_DOWNLOAD_PATH + output_filename + ".csv")

    if debug:
        logger.info(f"saving catalogue_dfs to filepath: {CASDA_CSV_DOWNLOAD_PATH + output_filename}"+".csv")
        logger.info(f"catalogue_dfs: \n {catalogue_dfs}")
        
    catalogue_coords = SkyCoord(ra = np.array(catalogue_dfs['ra_deg_cont']) * un.deg,
                                dec = np.array(catalogue_dfs['dec_deg_cont']) * un.deg)
    seps = TARGET_SOURCE_COORDS.separation(catalogue_coords).to('arcsecond') 

    if debug:
        sorted_indices = seps.argsort()
        logger.info("10 lowest separations (arcsecs) bwtween target source and catalogue source in arcseconds:")
        for i in range(len(seps)):
            index = sorted_indices[i]
            sep = seps[index]
            catalogue_coord = catalogue_coords[index]
            logger.info(f"({i + 1:02d}): Separation (arcsecs): {sep.arcsecond:<20}, from catalogue source (ra, dec) in deg: ({catalogue_coord.ra.value}, {catalogue_coord.dec.value}), with filename: {catalogue_dfs['source_filename'][index]}")   
            if i > 10:
                break

    matches_indices = np.where(seps < SEARCH_RADIUS)[0]
    matches = catalogue_dfs.iloc[matches_indices]

    if debug:
        logger.info(f"final matches with all casda ({type(matches)}): \n {matches}")

    # ensure match directory exists
    if not os.path.exists(CASDA_MATCHES_PATH):
        os.makedirs(CASDA_MATCHES_PATH)

    matches.to_csv(CASDA_MATCHES_PATH + output_filename + ".csv", index=False) # NOTE: index=False tells panda to not create row index column

    if debug and matches.empty:
        logger.info(f"No matches found for source (ra, dec): ({source_ra},{source_dec})")
        return None
    
    return matches

if __name__ == "__main__":
    
    # username = input("Enter CASDA username:")
    # casda = Casda()
    # casda.login(username=username)
    
    # Tests
    # proper motion corrected exoplanets: (ra, dec). Taken from \\NASA_with_Proper_Motion
    proper_motion_corrected = {
        "HAT-P-20b": (111.91642107519333, 24.335970319603273),
        "HD88133b" : (152.53191687262913, 18.185318394978616)
    }

    # source = "HAT-P-20b"
    # ra, dec = proper_motion_corrected[source]
    test_df = pd.read_csv(".\\proxima_cen_b_test\\PS_2024.05.09_04.24.22.csv")
    test_data = test_df.iloc[0]
    test_ra = test_data['ra']
    test_dec = test_data['dec']
    # logger.info(test_ra, test_dec)
    logger.info(extract_epoch_from_pubdat_catalogue("selavy-image.i.VAST_1453-62.SB50301.cont.taylor.0.restored.conv.components.xml"))    
    # casda_search(test_ra,test_dec, 3, casda=casda, refresh=False, debug=True)
    # casda_search_closest_catalogue(test_ra,test_dec, casda=casda, refresh=False, debug=True)
    # casda_search(proper_motion_corrected["HAT-P-20b"][0],proper_motion_corrected["HAT-P-20b"][1], 3, casda=casda, refresh=False, debug=True)
    # casda_search(proxima_cent_b[0],proxima_cent_b[1], 3, casda=casda, refresh=False, debug=True)