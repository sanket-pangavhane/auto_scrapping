import requests
import os

def download_pdf(url, name, docket_number):
    download_folder = "/home/sanket/Desktop/browser_use_poc/upload"

    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Generate filename from parameters
    filename = f"{name}_{docket_number}.pdf"
    download_path = os.path.join(download_folder, filename)

    # Check if file already exists; if so, return path immediately
    if os.path.isfile(download_path):
        print("File already exists, returning existing file path:", download_path)
        return filename  # Return filename (consistent with later returns)

    # Simulate a browser by setting the User-Agent header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.36',
    }

    base_url = "https://ujsportal.pacourts.us"

    # Check and append base URL if needed
    if not url.startswith(base_url):
        full_url = base_url + url
    else:
        full_url = url

    print("Downloading from URL:", full_url)

    try:
        response = requests.get(full_url, headers=headers, stream=True)
        response.raise_for_status()

        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        # Verify download success by checking file size
        if os.path.isfile(download_path) and os.path.getsize(download_path) > 0:
            print("File downloaded successfully and saved to:", download_path)
            return filename
        else:
            print("Download failed or file is empty.")
            return None

    except requests.exceptions.RequestException as e:
        print("Error downloading the file:", e)
        return None

# Usage example:
# url = 'https://ujsportal.pacourts.us/Report/MdjDocketSheet?docketNumber=MJ-05247-NT-0000531-2022&dnh=yRre5jZuTSfpFC6B3nJBEg%3D%3D'
# name = 'CalhounKeith'
# ans = download_pdf(url=url, docket_number="JBSI1-23D", name=name)
# print("Downloaded file path:", ans)



















# import requests
# import os

# def download_pdf(url, name, docket_number):
#     download_folder = "/home/sanket/Desktop/browser_use_poc/upload"

#     # Ensure the download folder exists
#     if not os.path.exists(download_folder):
#         os.makedirs(download_folder)

#     # Generate filename from parameters
#     filename = f"{name}_{docket_number}.pdf"
#     download_path = os.path.join(download_folder, filename)

#     # Check if file already exists, if so return path immediately
#     if os.path.isfile(download_path):
#         print("File already exists, returning existing file path:", download_path)
#         return download_path

#     # Simulate a browser by setting the User-Agent header
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) '
#                       'Chrome/58.0.3029.110 Safari/537.36',
#     }

#     base_url = "https://ujsportal.pacourts.us"

#     # Check and append base URL if needed
#     if not url.startswith(base_url):
#         full_url = base_url + url
#     else:
#         full_url = url

#     print("Downloading from URL:", full_url)

#     try:
#         response = requests.get(full_url, headers=headers, stream=True)
#         response.raise_for_status()

#         with open(download_path, 'wb') as file:
#             for chunk in response.iter_content(chunk_size=1024):
#                 if chunk:
#                     file.write(chunk)

#         # Verify download success by checking file size
#         if os.path.isfile(download_path) and os.path.getsize(download_path) > 0:
#             print("File downloaded successfully and saved to:", download_path)
#             return filename
#         else:
#             print("Download failed or file is empty.")
#             return None

#     except requests.exceptions.RequestException as e:
#         print("Error downloading the file:", e)
#         return None

