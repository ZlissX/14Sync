from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDRectangleFlatButton,MDFlatButton
from kivymd.uix.screen import Screen
from tkinter.filedialog import askdirectory
from tkinter import Tk
from kivymd.uix.dialog import MDDialog
import time
import os
import shutil
from pydrive.auth import GoogleAuth#this is to import google auth
from pydrive.drive import GoogleDrive#this will import the google drive module


class MainApp(MDApp):
    def build(self):
        screen = Screen()
        btn1 = MDRectangleFlatButton(text='Select Client No', pos_hint={'center_x': 0.5, 'center_y': 0.5},on_release=self.select_client_no)

        

        btn3 = MDRectangleFlatButton(text='Import', pos_hint={'center_x': 0.2, 'center_y': 0.5},on_release=self.func_imp)

        

        btn2 = MDRectangleFlatButton(text='Start', pos_hint={'center_x': 0.8, 'center_y': 0.5},on_release=self.run_prog)

        screen.add_widget(btn3)                            
        screen.add_widget(btn2)
        screen.add_widget(btn1)
        return screen
    def func_imp(self,obj):
        global path
        root=Tk()
        path=askdirectory(title="Please select a directory to import")
        root.update()
        root.destroy()
    def select_client_no(self,obj):
        self.dialog = MDDialog(title='Select a client no',
                               size_hint=(0.8, 1),
                               buttons=[MDRectangleFlatButton(text='2', on_release=self.press_2),
                                        MDRectangleFlatButton(text='1',on_release=self.press_1)])
        self.dialog.open()

    def press_1(self,obj):
        global clientno
        clientno="1"
        self.dialog.dismiss()

    def press_2(self,obj):
        global clientno
        clientno='2'
        self.dialog.dismiss()
    
    
    
    
    def run_prog(self,obj):
                
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
        
        def exist_notexist():#returns first or not first
            try:
                with open('mycreds.txt') as reader:
                    confirmsize=reader.read()
                    if confirmsize>2:
                        return 'not_first'
                    else:
                        return 'first'
        
            except:
                return 'first'
        
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
                
        def file_delete(item_to_delete):#this fuction will be used to delete items
            os.remove(item_to_delete)
        
        
        
        
        
        
        
        #Syncing Part Starts here
        
        #this part will take care of signing in 
        signinvar=exist_notexist()
        
        if signinvar=='first':
            first_login()
        if signinvar=='not_first':
            not_first_login()
        
        
        
        #this part of the code will upload the os_file_list() files
        #clientno=input('Enter the client no : ')
        #path=askdirectory(title='Import the folder you want to sync')#after  done the tinkter window needs to be closed.
        
        
        folderPaths,filePaths= os_file_list(path)
        
        list_writer(folderPaths,'folderpath'+clientno)#rememeber folderpath.
        list_writer(filePaths,'filepath'+clientno)#remeber file path.
        
        file_upload('folderpath'+clientno+'.txt')#this will upload the files to the drivev.
        file_upload('filepath'+clientno+'.txt')#this will upload the files to the drive.
        
        file_delete('folderpath'+clientno+'.txt')#this will delete file paths from the pc.
        file_delete('filepath'+clientno+'.txt')#this will delete file paths from the pc.
        
        
        
        #This part of the code will download the file paths from the other client.
        
        if clientno=='1':
            opp_clientno='2'
        
        if clientno=='2':
            opp_clientno='1'
        #we never need to think about the oppsite client no again.
        file_download('folderpath'+opp_clientno+'.txt')
        file_download('filepath'+opp_clientno+'.txt')
        
        #this part of the code will convert the downloaded files into lists
        files_from_the_other_client=list_reader('filepath'+opp_clientno+'.txt')
        folders_from_the_other_client=list_reader('folderpath'+opp_clientno+'.txt')
        
        file_delete('folderpath'+opp_clientno+'.txt')
        file_delete('filepath'+opp_clientno+'.txt')
        
        
        #this part of the code will compare the lists from  the other client and this client:
        missing_files_from_this_client=list()
        missing_folders_from_this_client=list()
        #this will filter the files
        for item in files_from_the_other_client:
            if item not in filepaths_of_client:
                missing_files_from_this_client.append(item)
        #this will filter the folder
        for item in folders_from_the_other_client:
            if item not in folderpaths_of_client:
                missing_folders_from_this_client.append(item)
        
        
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
        
        for item in missing_folders_from_this_client:
            if item=='':
                continue
            os.mkdir(path+item)
        
        
        if clientno=='1':
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
                file_download(file)
                while True:
                    try:
                        shutil.move(os.getcwd()+'\\'+file,path+item[:subtract_file_name])
                        log_client(os.getcwd()+'\\'+file+'\n',path+item[:subtract_file_name])
                        break
                    except:
                        log_client(os.getcwd()+'\\'+file+'\n',path+item[:subtract_file_name])
        
        
        
        if clientno=='2':
            for item in missing_files_from_this_client:
                if item=='':
                    continue
                name_splitter=item.split('\\')
                file=name_splitter[-1]
                subtract_file_name=len(item)-len(file)
                file_download(file)
                while True:
                    try:
                        shutil.move(os.getcwd()+'\\'+file,path+item[:subtract_file_name])
                        log_client(os.getcwd()+'\\'+file+'\n',path+item[:subtract_file_name])
                        break
                    except:
                        log_client(os.getcwd()+'\\'+file+'\n',path+item[:subtract_file_name])
        
        
            #this part will take care of uploading
            for item in files_to_upload:
                if item=='':
                    continue
                file_upload(path+item) #we might need to move the upload files to the actual path.

        

MainApp().run()