# Upload videos to Kaltura from course subfolders.

import os,logging,datetime
import csv,json
import pandas as pd
from KalturaClient import *
from KalturaClient.Plugins.Core import *

config = KalturaConfiguration()
client = KalturaClient(config)
secret = ""   # Enter your secret
user_id = ""  # Enter your Kaltura user id
k_type = KalturaSessionType.ADMIN
partner_id = "" # Enter your partner id
expiry = 86400
privileges = ""

ks = client.session.start(secret, user_id, k_type, partner_id, expiry, privileges)
client.setKs(ks)

now = datetime.datetime.now()

def kaltura_get_category(categoryParentId, categoryName):
    pager = KalturaFilterPager()
    kcf = KalturaCategoryFilter()
    kcf.ancestorIdIn = categoryParentId
    kcf.nameOrReferenceIdStartsWith  = categoryName
    try:
        kcf_result = client.category.list(kcf, pager).objects
    except Exception as ex:
        print(ex)
    return(kcf_result[0].id)

def kaltura_create_parent_category(courseId):
    kaltura_course_category_id = ""
    course_category = KalturaCategory()
    course_category.name = courseId
    course_category.parentId = ""    # Enter the parent Id
    try:
        course_category_result = client.category.add(course_category)
        kaltura_course_category_id = course_category_result.id
    except Exception as e:
        print(e)
        kaltura_course_category_id = kaltura_get_category(course_category.parentId, course_category.name)

    inContext_course_category_id = ""
    inContext_category = KalturaCategory()
    inContext_category.name = "InContext"
    inContext_category.parentId = kaltura_course_category_id # Canvas/site/channels/<course id>

    try:
        inContext_category_result = client.category.add(inContext_category)
        inContext_course_category_id = inContext_category_result.id
    except Exception:
        inContext_course_category_id = kaltura_get_category(inContext_category.parentId, inContext_category.name)

    return(inContext_course_category_id)

def kaltura_add_to_category(categoryId, entryId):
    category_entry = KalturaCategoryEntry()
    category_entry.categoryId = categoryId
    category_entry.entryId = entryId
    category_entry_result = client.categoryEntry.add(category_entry)

def kaltura_upload(media_file, media_title, category, creator):
    upload_token = KalturaUploadToken()
    token = client.uploadToken.add(upload_token);
    upload_token_id = token.id
    file_data =  open(media_file, 'rb')
    resume = False
    final_chunk = True
    resume_at = -1
    result = client.uploadToken.upload(upload_token_id, file_data, resume, final_chunk, resume_at)
    media_entry = KalturaMediaEntry()
    media_entry.name = media_title
    media_entry.description = creator
    media_entry.mediaType = KalturaMediaType.VIDEO
    media_entry.userId = creator
    media_entry.creatorId = creator # Should be the same as the userId
    media_entry.entitledUsersPublish = ""
    media_entry.adminTags = "Extracted from Blackboard Archive"
    media_entry.categories = ""
    entry = client.media.add(media_entry)
    entry_id = entry.id
    resource = KalturaUploadedFileTokenResource()
    resource.token = upload_token_id

    entry = client.media.addContent(entry_id, resource)
    print("Entry: " + entry.id)
    return(entry.id)

def getCourseInstructorList(filePath):
    media_csv = pd.read_csv(filePath)
    media_data = media_csv.set_index("Name", drop=False)
    print(media_data.head())
    return(media_data)

def upload_video(dir, media_data):
    media_dir = os.path.join(dir,"archives_media_courses")
    extracted_courses = os.listdir(media_dir)
    for course in extracted_courses:
        if not course.startswith('.'):
            searchString = "ArchiveFile_" + course + ".zip"
            if(searchString in media_data['Name'].values):
                print(media_data[media_data.Name==searchString][['banner_1']])
                print("Found " + course + " in dataframe")
                # Create the parent categories
                category_id = kaltura_create_parent_category(course)
                course_path = os.path.join(media_dir,course)
                course_media = os.listdir(os.path.join(media_dir,course))
                for media_file in course_media:
                    media_path = os.path.join(course_path,media_file)
                    print("Path to file: ")
                    print(media_path)
                    # This assigns the tuple - need to only get the id
                    owner = media_data[media_data.Name==searchString]['banner_1']
                    print(owner)
                    entry_id = kaltura_upload(media_path, media_file, course, owner[0])
                    kaltura_add_to_category(category_id, entry_id)
            else:
                print("Did not find " + course + " in dataframe")

if __name__ == '__main__':
    root_dir = input("Enter the starting directory path:\t")
    media_data = getCourseInstructorList("media_term_202001.csv")
    upload_video(root_dir, media_data)
