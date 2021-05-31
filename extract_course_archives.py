import os, zipfile,logging,datetime

# The archives or zip files should be stored in a folder <rootdir>\archives

def extract_courses(dir):

    now = datetime.datetime.now()

    archive_path = os.path.join(dir,"archives")
    deflate_path = os.path.join(dir, "archives_extracted")
    processed_path = os.path.join(dir, "archives_processed")
    failed_path = os.path.join(dir, "archives_failed")

    course_archives = os.listdir(archive_path)
    for archive in course_archives:
        if archive.lower().endswith(".zip"):

            logName = "./logs/deflate/" + now.strftime("%Y-%m-%d %H:%M:%S") + "_deflate.log"
            logging.basicConfig(filename=logName,level=logging.INFO)
            current_archive_path = os.path.join(archive_path, archive)
            current_archive_processed_path = os.path.join(processed_path, archive)
            current_archive_failed_path = os.path.join(failed_path, archive)

            current_archive = zipfile.ZipFile(current_archive_path, 'r', allowZip64=True)
            if current_archive.testzip() == None:
                try:
                    archive_sub_1 = archive.replace('ArchiveFile_', '')
                    archive_sub_2 = archive_sub_1.replace('.zip','')
                    archive_deflated_path = os.path.join(deflate_path, archive_sub_2)
                    # current_archive.extractall(deflate_path + "/" + archive_sub_2)
                    current_archive.extractall(archive_deflated_path)
                    os.renames(current_archive_path, current_archive_processed_path)
                    print(archive + " deflated")
                    logging.info(archive + " deflated ")
                except zipfile.BadZipFile:
                    print("Couldn't unzip " + archive)
                    logging.info(archive + " ******* error ******* could not deflate")
                    os.renames(current_archive_path, current_archive_failed_path)
                    continue
                except zipfile.LargeZipFile:
                    print("Couldn't unzip " + archive)
                    logging.info(archive + " ******* error ******* too large")
                    os.renames(current_archive_path, current_archive_failed_path)
                    continue
            else:
                os.renames(current_archive_path, current_archive_failed_path)
                print(print("Couldn't unzip " + archive))
                logging.info(archive + " failed test")

            current_archive.close()


if __name__ == '__main__':
    root_dir = input("Enter the starting directory path:\t")
    extract_courses(root_dir)
