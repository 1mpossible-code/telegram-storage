import logging
import os
from Bot import Bot
from Files import Files


class App:
    def __init__(self) -> None:
        self.bot = Bot()
        self.files = Files("db.sqlite")

    async def send_file(self, file_path: str) -> None:
        # if the file is greater than 2000MB, we will split it into multiple files and send them separately
        if os.path.getsize(file_path) > 2000 * 1024 * 1024:
            logging.info("File too large, splitting...")
            file_name = os.path.basename(file_path)
            file_dir = "temp"
            # split file into 2000MB chunks
            os.system(f"split -b 2000M {file_path} {file_dir}/{file_name}_")
            # get all files in the directory
            files = os.listdir("temp")
            # sort the files by their letter: _aa, _ab, _ac, etc.
            files.sort()
            # send each file
            msg_ids = []
            file_ids = []
            for file in files:
                msg_id, file_id = await self.bot.send_file(os.path.join(file_dir, file))
                msg_ids.append(msg_id)
                file_ids.append(file_id)
            # record the files in the db
            self.files.insert_file(file_path, msg_ids, file_ids, os.path.getsize(file_path))
            logging.info("File sent and recorded")
            # clean up the directory
            os.system(f"rm -rf {file_dir}/*")
        else:
            msg_id, file_id = await self.bot.send_file(file_path)
            self.files.insert_file(file_path, msg_id, file_id, os.path.getsize(file_path))
            logging.info("File sent and recorded")

    async def get_file_content(self, uid: int) -> str:
        f = self.files.get_file(uid)
        file_ids = f[3]
        if "," in file_ids:
            file_ids = file_ids.split(",")
        else:
            file_ids = [file_ids]
        content = bytes()
        for file_id in file_ids:
            content += await self.bot.get_file(file_id)
        logging.info("File content received")
        return content

    async def save_file(self, uid: int, dir: str = "./temp") -> None:
        content = await self.get_file_content(uid)
        f = self.files.get_file(uid)
        file_name = f[1]
        file_path = os.path.join(dir, file_name)
        # check if directory exists
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(file_path, "wb") as file:
            file.write(content)
        logging.info("File saved")

    async def get_all_files(self) -> list:
        return self.files.get_all_files()

    async def delete_file(self, uid: str) -> None:
        f = self.files.get_file(uid)
        message_ids = f[2]
        # delete all messages associated with the file
        if "," in message_ids:
            message_ids = message_ids.split(",")
        else:
            message_ids = [message_ids]
        for message_id in message_ids:
            await self.bot.delete_file(int(message_id))
            self.files.remove_file(uid)
            logging.info("Message deleted with id " + message_id)
        logging.info(f"File deleted and removed from db: {uid}")
