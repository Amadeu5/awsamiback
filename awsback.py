#!/usr/bin/python

import boto3
import datetime
import time
import sys

#high-level connection to EC2
ec2 = boto3.resource('ec2')

#text painted as usual
sys.stdout.write("\033[0;0m")
#backup rotation 7 days = 10080/(60*24) - time in minutes
backup_rotation = 10080

print ("* BAKCUP STARTED")

#check instance connection
if (ec2 is None):
    print ("** Connection to instance is FAILURE\n")
else:
    print ("** Connection to instance is OK\n")

#filter instances by tag name:Backup and value:true
    filtred_instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:Backup', 'Values': ['true']}])
    for instance in filtred_instances:

        datetime_now = datetime.datetime.now()
        date_format = datetime_now.strftime("%Y-%m-%d_%H-%M__")
        #created humanreadeble name for image
        bak_ami_name = date_format + instance.id + "_bak"

        #trying to create new backup image with tags
        try:
            bak_ami_id = instance.create_image(Name=bak_ami_name, NoReboot=True, DryRun=False)
        except Exception, e:
            print('Backup ' + instance.id + ' : ' + e.message)
            continue

        print ('Image: ' + bak_ami_name + ' - CREATED')

        #write tags in image
        images = ec2.images.filter(Owners=['self'])
        for image in images:
            image.create_tags(Tags=[
            {
                'Key': 'Name',
                'Value': image.name
            }])

#deletign images that old than 7 days and painting list of images
            # text painted as usual
            sys.stdout.write("\033[0;0m")
            #create datetime from string
            #name tag used instead creation.date tag because time error
            image_creation_datetime = datetime.datetime.strptime(str(image.name)[:16], "%Y-%m-%d_%H-%M")

            #create timestamp from current time datetime format
            datetime_now_timestamp = time.mktime(datetime_now.timetuple())

            #datetime to timestamp
            image_creation_timestamp = time.mktime(image_creation_datetime.timetuple())

            #difference in minutes
            diff_minutes = int((datetime_now_timestamp - image_creation_timestamp)/60)

            #temporary variable for image.name
            tmp_image_name = image.name
            #if older than 7 days
            if (diff_minutes >= backup_rotation):
                #deregister older backup image
                image.deregister(DryRun=False)
                #text painted red
                sys.stdout.write("\033[1;31m")
                print("Image: " + tmp_image_name + " - DELETED")
            #older than 5 days
            elif (diff_minutes >= 7200):
                #text painted yellow
                sys.stdout.write("\033[1;33m")
                print('Image: ' + tmp_image_name)
            #newer than 2 days
            elif (diff_minutes < 2880 ):
                #text painted green
                sys.stdout.write("\033[0;32m")
                print('Image: ' + tmp_image_name)
            #other else images
            else:
                #text painted as usual
                sys.stdout.write("\033[0;0m")
                print('Image: ' + tmp_image_name)

#text painted as usual
sys.stdout.write("\033[0;0m")
print ("* BAKCUP ENDED")