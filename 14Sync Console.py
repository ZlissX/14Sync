import pydrive
import shutil
import os
import time
from tkinter import Tk,TRUE,FALSE,Label,Frame,Button,COMMAND,Image,mainloop,PhotoImage,FLAT,TOP,LEFT,BOTH
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tkinter.filedialog  import askdirectory
from threading import Thread


#clientno=the actual clientno
#opossiteclientno=oppsite client no
def first_login():#this function will be used when a user needs to login  for the first time.
    global drive

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)

def not_first_login():#this function will be used when a user had already logged in before.
    global drive
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    drive=GoogleDrive(gauth)

def login():#returns first or not first

    temp_list_for_login=os.listdir(os.getcwd())
    if "mycreds.txt" in temp_list_for_login:
        not_first_login()
    else:
        first_login()


#this will upload the files
def file_upload(item_file):
    
    upload_file = drive.CreateFile()
    upload_file.SetContentFile(item_file) #load local file data into the File instance
    upload_file.Upload()  #creates a file in your drive with the name: my-awesome-file.txt
#this will delete the files in the drive
def filedelete(item_file):
    file_list = drive.ListFile({'q': "title contains "+"'"+item_file+"'"+" and trashed=false"}).GetList() #find the file using file name.
    file_id = file_list[0]['id'] #get the file ID.
    file = drive.CreateFile({'id': file_id})
    file.Delete()
#this will get the paths of the clients and convert them to lists
def os_file_list(path_of_the_folder_to_sync):#the outpu will be recived in two varaibles the first one in the folder paths list and the second part is the file paths list
    global folderpaths_of_client
    global filepaths_of_client
    
    folderpaths_of_client=list()
    filepaths_of_client=list()

#this will walk through all the folders and subfolders to gather the file paths
    for folders,subfolders,files in os.walk(path_of_the_folder_to_sync):#Make a fuction for path!
            folderpaths_of_client.append(folders[len(path_of_the_folder_to_sync):])
            
            
            for file in files:
                filepaths_of_client.append(folders[len(path_of_the_folder_to_sync):]+"\\"+file)
    folderpaths_of_client.sort()
    filepaths_of_client.sort()           
    return folderpaths_of_client,filepaths_of_client

def list_writer(list_you_want_to_write_into_a_text_file,nameofthedoc):#you need to give the list first and then the name of the document or textfile
    with open(nameofthedoc+'.txt','w') as write_handler:
        for item in list_you_want_to_write_into_a_text_file:
            write_handler.write(item+'\n')#this will write the files/paths in order.


#This function takes in the document files and converts them to a list.
def list_reader(filename_of_the_textfile):#this will return a list.
    try:
        with open(filename_of_the_textfile,'r') as reader_handle:
            tempreader=reader_handle.read()
            return tempreader.split('\n')
    except:
        log_client('failed to open in list_reader',filename_of_the_textfile)

def log_client(string,string2optional=''):#can take in two strings ,second strings default value is None.
    with open('logfile.txt','a+') as log_writer:
        log_writer.write(string+' '+string2optional+'\n')

def copy_file(copyname,copypath):
    shutil.copy2(copyname,copypath)

def file_download(item_to_download): #downloading the files from the drive
    downloadtry=0
    while True:
        try:
            time.sleep(2)
            file_list = drive.ListFile({'q': "title contains "+"'"+item_to_download+"'"+" and trashed=false"}).GetList()#find the file using file name.
            file_id = file_list[0]['id'] # get the file ID.
            file = drive.CreateFile({'id': file_id})
            file.GetContentFile(item_to_download) # downloads the file content and file.
            file.Delete()
            break
        except: #skips the download of the files if the tryies exceed 3 times.
            
            log_client('failed to download :',item_to_download)
            continue
            '''downloadtry+=1
            if downloadtry>=10:
                downloadtry=0
                break'''



def fldownload(temppath,item_to_download): #downloading the files from the drive/this will download the files in temp folder
    downloadtry=0
    while True:
        try:
            time.sleep(2)
            file_list = drive.ListFile({'q': "title contains "+"'"+item_to_download+"'"+" and trashed=false"}).GetList()#find the file using file name.
            file_id = file_list[0]['id'] # get the file ID.
            file = drive.CreateFile({'id': file_id})
            file.GetContentFile(temppath+'//'+item_to_download) # downloads the file content and file.
            file.Delete()
            break
        except: #skips the download of the files if the tryies exceed 3 times.
            
            log_client('failed to download :',temppath+'//'+item_to_download)
            continue
            '''downloadtry+=1
            if downloadtry>=10:
                downloadtry=0
                break'''


def mtime_logger():
    folderPaths,filePaths= os_file_list(path)
    file_paths_with_mtime=list()
    file_paths_for_del_check=list()
    for item in filePaths:#this will attatch mytime to the items and write a log.
        if item =='\n' or item =='':
            continue
        file_paths_with_mtime.append(item+'|'+str(os.path.getmtime(path+'\\'+item)))
    list_writer(file_paths_with_mtime,'original mtime log')#optional can do this if you want to save memory but make sure that you clear the list or it won't save any memory
    for item in filePaths:#this will make a list so the delete file log can keep verifying the files.
        if item =='\n' or item =='':
            continue
        file_paths_for_del_check.append(item)
    list_writer(file_paths_for_del_check,'orgninal del log file')#optional can do this if you want to save memory but make sure that you clear the list or it won't save any memory

def run_writer_start(filename):
        with open("running_status_files_don't delete\\"+filename+'.txt','w') as sync_handler:
            sync_handler.write('Running')

def run_writer_end(filename):
        with open("running_status_files_don't delete\\"+filename+'.txt','w') as sync_handler:
            sync_handler.write('Not Running')

def run_checker(filename):
    with open("running_status_files_don't delete\\"+filename+'.txt') as sync_handler:
        temp_var=sync_handler.read()
        if 'Running' == temp_var:
            return True
        if 'Not Running' == temp_var:
            return False

    
        
def file_delete(item_to_delete):#this fuction will be used to delete items
    os.remove(item_to_delete)

def initlogs():
    try:
        os.mkdir("running_status_files_don't delete\\")
    except:
        pass

    run_writer_end('del_file_checker_run_file')
    run_writer_end('filesyncer_progress')
    run_writer_end('m_time_checker_run_file')
    run_writer_end('m_time_listner_checker_run_file')






#Syncing Part Starts here

#this part will take care of signing in

login()

initlogs()

#this part of the code will upload the os_file_list() files
clientno=input('Enter the client no : ')
path=askdirectory(title='Import the folder you want to sync')#after  done the tinkter window needs to be closed.
temppath=os.getcwd()+'\\temp_folder_for_syncer'#after  done the tinkter window needs to be closed.

mtime_logger()


def folder_syncer():
    folderPaths,filePaths= os_file_list(path)

    list_writer(folderPaths,'folderpath'+clientno)#rememeber folderpath.

    file_upload('folderpath'+clientno+'.txt')#this will upload the files to the drivev.

    file_delete('folderpath'+clientno+'.txt')#this will delete file paths from the pc.



    #This part of the code will download the file paths from the other client.

    if clientno=='1':
        opp_clientno='2'

    if clientno=='2':
        opp_clientno='1'
    #we never need to think about the oppsite client no again.
    file_download('folderpath'+opp_clientno+'.txt')

    #this part of the code will convert the downloaded files into lists
    folders_from_the_other_client=list_reader('folderpath'+opp_clientno+'.txt')

    file_delete('folderpath'+opp_clientno+'.txt')


    #this part of the code will compare the lists from  the other client and this client:
    missing_folders_from_this_client=list()
    #this will filter the folder
    for item in folders_from_the_other_client:
        if item not in folderpaths_of_client:
            missing_folders_from_this_client.append(item)



    #This is the part of code where folders/files will start Syncing.

    for item in missing_folders_from_this_client:
        if item=='':
            continue
        try:
            os.mkdir(path+item)
        except:
            pass




def file_syncer():
    folderPaths,filePaths= os_file_list(path)

    run_writer_start('filesyncer_progress')

    list_writer(filePaths,'filepath'+clientno)#remeber file path.
    file_upload('filepath'+clientno+'.txt')#this will upload the files to the drive.
    file_delete('filepath'+clientno+'.txt')#this will delete file paths from the pc.



    #This part of the code will download the file paths from the other client.

    if clientno=='1':
        opp_clientno='2'

    if clientno=='2':
        opp_clientno='1'
    #we never need to think about the oppsite client no again.
    file_download('filepath'+opp_clientno+'.txt')

    #this part of the code will convert the downloaded files into lists
    files_from_the_other_client=list_reader('filepath'+opp_clientno+'.txt')
    file_delete('filepath'+opp_clientno+'.txt')


    #this part of the code will compare the lists from  the other client and this client:
    missing_files_from_this_client=list()
    #this will filter the files
    for item in files_from_the_other_client:
        if item not in filepaths_of_client:
            missing_files_from_this_client.append(item)

    #this part of the code will upload the filelist missing on this client.

    #making a list of files that the other client needs to upload

    list_writer(missing_files_from_this_client,'filestoupload'+clientno)
    file_upload('filestoupload'+clientno+'.txt')
    file_delete('filestoupload'+clientno+'.txt')




    #this part of the code will download the uploadfilelist 

    file_download('filestoupload'+opp_clientno+'.txt')
    files_to_upload=list_reader('filestoupload'+opp_clientno+'.txt')
    file_delete('filestoupload'+opp_clientno+'.txt')
    files_to_upload.sort()



    #This is the part of code where folders/files will start Syncing.


    if clientno=='1':
        try:
            os.mkdir(temppath)
        except:
            pass
        #this part will take care of uploading
        for item in files_to_upload:
            if item=='':
                continue
            file_upload(path+item) #we might need to move the upload files to the actual path.


    #this part will take care of the downloads
        for item in missing_files_from_this_client:
            if item=='':
                continue
            name_splitter=item.split('\\')
            file=name_splitter[-1]
            subtract_file_name=len(item)-len(file)
            fldownload(temppath,file)
            while True:
                try:
                    shutil.move(temppath+'\\'+file,path+item[:subtract_file_name])
                    log_client('Copied the file in :'+temppath+'\\'+file+'\n',path+item[:subtract_file_name])
                    break
                except:
                    log_client('failed to copy the file in :'+temppath+'\\'+file+'\n',path+item[:subtract_file_name])



    if clientno=='2':
        try:
            os.mkdir(temppath)
        except:
            log_client('File Already Exists')
    #this part will take care of the downloads
        for item in missing_files_from_this_client:
            if item=='':
                continue
            name_splitter=item.split('\\')
            file=name_splitter[-1]
            subtract_file_name=len(item)-len(file)
            fldownload(temppath,file)
            while True:
                try:
                    shutil.move(temppath+'\\'+file,path+item[:subtract_file_name])
                    log_client('Copied the file in :'+temppath+'\\'+file+'\n',path+item[:subtract_file_name])
                    break
                except:
                    log_client('failed to copy the file in :'+temppath+'\\'+file+'\n',path+item[:subtract_file_name])


        #this part will take care of uploading
        for item in files_to_upload:
            if item=='':
                continue
            file_upload(path+item) #we might need to move the upload files to the actual path.

    with open('main_file_sync_verifier'+clientno+".txt",'w') as random_handler:
        random_handler.write('')
    file_upload('main_file_sync_verifier'+clientno+".txt")
    file_delete('main_file_sync_verifier'+clientno+".txt")

    file_download('main_file_sync_verifier'+opp_clientno+".txt")
    file_delete('main_file_sync_verifier'+opp_clientno+".txt")

    run_writer_end('filesyncer_progress')    







def mtime_checker():
    time.sleep(5)
    #it should then check for modified time diffrence if it finds a modified time diffrence it should upload the files to the other client.
    #note the whole mtime will be in a sync it will restart the loop only if there are new files.

    while True:
        folder_syncer()
        file_syncer()
        mtime_logger()

        time.sleep(3)
        checker_for_flsync=run_checker('filesyncer_progress')
        checker_for_mlistener=run_checker('m_time_listner_checker_run_file')
        checker_for_delrunchecker=run_checker('del_file_checker_run_file')


        if checker_for_flsync==True:
            continue
        
        if checker_for_mlistener==True:
            continue
        if checker_for_delrunchecker==True:
            continue


        run_writer_start('m_time_checker_run_file')



        with open('sync_from_m_time_sync_first'+clientno+'.txt','w') as handler:
            handler.write('')
        file_upload('sync_from_m_time_sync_first'+clientno+'.txt')
        file_delete('sync_from_m_time_sync_first'+clientno+'.txt')
        if clientno=='1':
            opp_clientno='2'

        if clientno=='2':
            opp_clientno='1'
        #we never need to think about the oppsite client no again.
        file_download('sync_from_m_time_sync_first'+opp_clientno+'.txt')
        file_delete('sync_from_m_time_sync_first'+opp_clientno+'.txt')
        #this is where the mtime starts
        file_paths_with_mtime=list()
        file_paths_with_mtime=list_reader('original mtime log.txt')
        folderPaths,filePaths= os_file_list(path)
        temp_list_for_mtime_check=list()

        for item in filePaths:
            if item =='\n' or item =='' or None:
                continue
            temp_list_for_mtime_check.append(item+'|'+str(os.path.getmtime(path+'\\'+item)))
        mtime_diffrence_checker=set(temp_list_for_mtime_check)-set(file_paths_with_mtime)
        reset_value_for_mtimelog=0
        if len(mtime_diffrence_checker)!=0:
            reset_value_for_mtimelog=1
            mfile_temp=list(mtime_diffrence_checker)
            list_of_modified_files_to_upload=list()
            for item in mfile_temp:
                temp_list_holder=item.split('|')
                list_of_modified_files_to_upload.append(temp_list_holder[0])

            list_writer(list_of_modified_files_to_upload,'modified_files__'+clientno)
            file_upload('modified_files__'+clientno+'.txt')
            file_delete('modified_files__'+clientno+'.txt')
            #This part of the code will take care of uploading the files.
            for item in list_of_modified_files_to_upload:
                file_upload(path+item)        
                if clientno=='1':
                    opp_clientno='2'

                if clientno=='2':
                    opp_clientno='1'
                #we never need to think about the oppsite client no again.
            file_download('m_time_module_completed'+opp_clientno+'.txt')
            file_delete('m_time_module_completed'+opp_clientno+'.txt')
        


        with open('sync_from_m_time_sync'+clientno+'.txt','w') as handler:
            handler.write('')
        file_upload('sync_from_m_time_sync'+clientno+'.txt')
        file_delete('sync_from_m_time_sync'+clientno+'.txt')
        if clientno=='1':
            opp_clientno='2'

        if clientno=='2':
            opp_clientno='1'
        #we never need to think about the oppsite client no again.
        file_download('sync_from_m_time_sync'+opp_clientno+'.txt')
        file_delete('sync_from_m_time_sync'+opp_clientno+'.txt')
        if reset_value_for_mtimelog==1:
            mtime_logger()
            

        delete_checker()
        run_writer_end('m_time_checker_run_file')
        






def delete_checker():#this is the file delete checker
    #1.it should check for delete files and delete them of both the clients
    #2.it should then check for new files and if it does,it should then it should call the syncer again.
    if clientno=='1':
        opp_clientno='2'

    if clientno=='2':
        opp_clientno='1'
    #we never need to think about the oppsite client no again.

    run_writer_start('delete_checker_run_file')
    folderPaths,filePaths= os_file_list(path)
    file_paths_for_del_check=list_reader('orgninal del log file.txt')
    logged_file_paths=list()
    temp_list_for_del_check=list()
    for item in file_paths_for_del_check:
        if item =='\n' or item =='':
            continue
        logged_file_paths.append(item)

    
    for item in filePaths:
        if item =='\n' or item =='':
            continue
        temp_list_for_del_check.append(item)
    diffrence_checker=set(logged_file_paths)-set(temp_list_for_del_check)
    if len(diffrence_checker)!=0:#Once deleted files are spotted than this will happen.
       delUploadList=list(diffrence_checker)
       list_writer(delUploadList,'files_to_delete'+clientno)
       file_upload('files_to_delete'+clientno+'.txt')
       file_delete('files_to_delete'+clientno+'.txt')
    
       
    mtime_logger()
    with open('deletecheck_for_client'+clientno+'.txt','w') as handler:
        handler.write('')
    file_upload('deletecheck_for_client'+clientno+'.txt')    
    file_delete('deletecheck_for_client'+clientno+'.txt')

    file_download('deletecheck_for_client'+opp_clientno+'.txt')
    file_delete('deletecheck_for_client'+opp_clientno+'.txt')

        

        



def mtime_listener():#this will download the modified file from the other client.
    

    while True:
        checker_for_flsync=run_checker('filesyncer_progress')
        if checker_for_flsync==True:
            continue

        try:
            os.mkdir(temppath)
        except:
            log_client('File Already Exists')


        if clientno=='1':
            opp_clientno='2'

        if clientno=='2':
            opp_clientno='1'
        #we never need to think about the oppsite client no again.


        file_download('modified_files__'+opp_clientno+'.txt')
        run_writer_start('m_time_listner_checker_run_file')
        modified_files_to_download=list()
        modified_files_to_download=list_reader('modified_files__'+opp_clientno+'.txt')
        file_delete('modified_files__'+opp_clientno+'.txt')
        for item in modified_files_to_download:
            try :
                os.remove(path+item)
            except:
                log_client('Error :Failed to remove file',path+item)
            if item =='\n' or item =='':#this is a filter
                continue
            name_splitter=item.split('\\')
            file=name_splitter[-1]
            subtract_file_name=len(item)-len(file)
            fldownload(temppath,file)
            while True:
                try:
                    shutil.move(temppath+'\\'+file,path+item[:subtract_file_name])
                    log_client('Copied the file in :'+temppath+'\\'+file+'\n',path+item[:subtract_file_name])
                    break
                except:
                    log_client('failed to copy the file in :'+temppath+'\\'+file+'\n',path+item[:subtract_file_name])
        mtime_logger()
        with open('m_time_module_completed'+clientno+'.txt','w') as handler:
            handler.write(clientno)
        file_upload('m_time_module_completed'+clientno+'.txt')
        file_delete('m_time_module_completed'+clientno+'.txt')
        run_writer_end('m_time_listner_checker_run_file')

def delete_listner():
    

    while True:
        time.sleep(1)
        checker_for_flsync=run_checker('filesyncer_progress')
        if checker_for_flsync==True:
            continue

        if clientno=='1':
            opp_clientno='2'

        if clientno=='2':
            opp_clientno='1'
        #we never need to think about the oppsite client no again.
        file_download('files_to_delete'+opp_clientno+'.txt')
        run_writer_start('del_file_checker_run_file')
        list_of_files_to_delete=list()
        list_of_files_to_delete=list_reader('files_to_delete'+opp_clientno+'.txt')
        file_delete('files_to_delete'+opp_clientno+'.txt')

        for item in list_of_files_to_delete:
            if item =='\n' or item =='':#this is a filter
                continue
            try:#to make sure its not gonna crash the program
                os.remove(path+'\\'+item)

            except:
                log_client('Error : Failed to delete',item)
        run_writer_end('del_file_checker_run_file')

thread1=Thread(target=mtime_listener)
thread2=Thread(target=mtime_checker)
thread3=Thread(target=delete_listner)
thread1.start()
time.sleep(3)
thread2.start()
time.sleep(4)
thread3.start()
 

