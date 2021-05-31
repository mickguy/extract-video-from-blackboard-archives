# Search and extract video from Blackboard courses
# Once video removed from course package re-package.
# *********************************************


from pathlib import Path
import os, re, zipfile, shutil, fnmatch, logging, datetime

def crawl_dir(dir):
    now = datetime.datetime.now()
    logName = "./logs/extract_media/" + now.strftime("%Y-%m-%d %H:%M:%S") + ".log"
    output_path = dir + "/" + "archives_extracted"

    extracted_archives = os.listdir(output_path)
    extracted_path = ""
    for course in extracted_archives:
        if not course.startswith('.'):
            print(course)
            extracted_path = os.path.join(output_path, course)
            home_dir = os.path.join(output_path,course,"csfiles/home_dir")
            print(home_dir)
            media_moved = os.path.join(dir,"archives_media_courses",course)
            search_pattern = "*.mp4"

            for dirpath, dirname, files in os.walk(home_dir):
                curdir = f'{dirpath}'
                for f in files:
                    if f.lower().endswith(('.mp4', '.m4p','.m4v','.mkv','.mov','.qt','.avi', 'asf' '.wmv','wma','.webm', '.mpeg', '.mpg','.m1v', '.m2v','.flv', '.f4v', '.ogg', '.ogm', '.ogv', '.wav')):
                        logging.basicConfig(filename=logName,level=logging.INFO)
                        file_path = os.path.join(dirpath,f)
                        dest_path = os.path.join(media_moved,f)
                        try:
                            os.renames(file_path, dest_path)
                            print (file_path + " moved to " + dest_path)
                            logging.info(file_path + " moved to " + dest_path)
                        except OSError:
                            print("Error while moving file")
            new_archive_path = dir + "/" + "new_archives/"
            print("Archiving " + course)
            shutil.make_archive(new_archive_path + '/' + course, 'zip', extracted_path)

if __name__ == '__main__':
    root_dir = input("Enter the starting directory path:\t")
    crawl_dir(root_dir)
