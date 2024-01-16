from flask import  request, jsonify,send_from_directory
import asyncio
from App import App
import os

class UploadsController:
    def __init__(self,):
        self.app = App()
        
        
    def __download(self,uid,file_info):
        asyncio.run(self.app.download_file(uid))
        res = send_from_directory(self.app.file_manager.files_dir, file_info[1], as_attachment=True)
        self.app.file_manager.clean_files_directory()
        return res
    
    
    def read(self,uid=None):    
        if request.method == 'GET':
            download = request.args.get('download')
            try:
                if uid:
                    file_info = self.app.get_file_info(uid)

                    if download:
                        return self.__download(uid,file_info)
                    return jsonify({'id': file_info[0], 'name': file_info[1], 'message_ids': file_info[2], 'file_ids': file_info[3], 'size': file_info[4]})
                else:
                    all_files_info = asyncio.run(self.app.get_all_files_info())
                    data_dict = [{'id': item[0], 'name': item[1], 'message_ids': item[2], 'file_ids': item[3], 'size': item[4]} for item in all_files_info]
                    return jsonify(data_dict)
            except ValueError:
                return jsonify({'error': f'Upload {uid} not found', 'message': 'invalid resource URI'}), 404
    
    def create(self):
        if 'file' not in request.files:
            return jsonify({"message": "No file part in the request"}), 400
        
        user_file = request.files['file']
        
        if user_file.filename == '':
            return jsonify({"message": "No selected file"}), 400
        else:
            user_file_path = os.path.join(self.app.file_manager.temp_dir, user_file.filename)
            user_file.save(user_file_path)
            asyncio.run(self.app.upload_file(user_file_path))
            self.app.file_manager.clean_temp_directory()
            return jsonify({"message": "File successfully uploaded"}), 200  
    
    def delete(self,uid):
        try:
            asyncio.run(self.app.delete_file(uid))
            return jsonify({"message": f"File {uid} successfully deleted!"}), 200
        except ValueError:
            return jsonify({'error': f'Upload {uid} not found', 'message': 'invalid resource URI'}), 404