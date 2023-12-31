import time
import os
import pathlib
from flask import send_from_directory

from database import mydb
from .User import User

'''
status:
0-private
1-public
'''

class File(User):
    def __init__(self,name_file,id_user,file=None):
        self.file = file
        self._name_file=name_file.replace(" ","")
        super().__init__(id=id_user)
        self.directory=pathlib.Path('Files')
        
    @property
    def name_file(self):
        file_info=self.get_file()
        if file_info==None:
            return None
        return file_info['name_file']
    
    def save_file(self):
        try:
            time_now = int(time.time())
            name = f'{time_now}{self._name_file}'  
            route= f'{self.directory}/{name}'   
            self.file.save(route)
            self.insert_file_base(name)
            return True
        except Exception as e:
            print("**ERRO::", e)
            return False
        
    def insert_file_base(self,name):
        try:
            if self._name_file and self.id:
                mycursor = mydb.cursor()
                mycursor.execute('INSERT INTO files (name_file,id_user,status) values(%s,%s,%s)',(name,self.id,0))
                mydb.commit()
                return True
            return False
        except EOFError as e:
            print(e)
            return False
        
    def remove_file(self):
        try:
            file_info = self.get_file()
            if file_info is None:
                raise Exception("Arquivo não encontrado.")
            
            name_file = file_info['name_file']
            arquivo = list(self.directory.glob(name_file))
            os.remove(arquivo[0])
            self.delete_file()
            return True
        except Exception as e:
            print("**ERRO::", e)
            return False

    def delete_file(self):
        try:
            if self._name_file:
                mycursor = mydb.cursor()
                mycursor.execute("DELETE FROM files WHERE name_file LIKE %s and id_user=%s", (f'%{self._name_file}%',self.id))
                mydb.commit()
                return True
            return False
        except EOFError as e:
            print(e)
            return False
    
    def get_file(self):
        try:
            if self._name_file and self.id:
                result = {}
                mycursor = mydb.cursor()
                mycursor.execute('SELECT * FROM files WHERE name_file LIKE %s and id_user=%s',(f'%{self._name_file}%',self.id))
                myresult = mycursor.fetchone()
                if myresult:
                    column_names = [column[0] for column in mycursor.description]
                    indexed_result = [(column_names[i], field) for i, field in enumerate(myresult)]
                    for column_name, field in indexed_result:
                        result[column_name] = field
                    return result
            return None
        except EOFError as e:
            print(e)
            return None
    
    def update_status(self,status):
        try:
            if self._name_file and self.id:
                file_info=self.get_file()
                mycursor = mydb.cursor()
                mycursor.execute('UPDATE files SET status=%s WHERE id_file=%s',(status,file_info['id_file']))
                mydb.commit()
                return True
            return False
        except EOFError as e:
            print(e)
            return False
    
    def get_file_path(self):
        file_info = self.get_file()
        arquivo = list(self.directory.glob(file_info['name_file']))
        self.file = arquivo[0]
        if arquivo:
            return str(arquivo[0])
        else:
            return 'Arquivo não encontrado'
    
    def type_file(self):
        if str(self.file).endswith('.jpg') or str(self.file).endswith('.jpeg'):
            return 'image/jpeg'
        elif str(self.file).endswith('.png'):
            return 'image/png'
        elif str(self.file).endswith('.mp4'):
            return 'video/mp4'
        elif str(self.file).endswith('.mp3'):
            return 'audio/mp3'
        else:
            return 'application/octet-stream'