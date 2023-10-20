import requests
from tqdm import tqdm


token_yandex = ''
token_vk = ''
users_id = ''


class VK:

   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = self.resolve_id(user_id)
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

   def resolve_id(self, user_id):
        if user_id.isdigit():
            return user_id 
        
        url = f'https://api.vk.com/method/utils.resolveScreenName?screen_name={user_id}&v=5.131&access_token={self.token}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                real_id = data['response']['object_id']
                return str(real_id)
            else:
                print('Ошибка при расшифровке сокращенного ID.')
        else:
            print(f'Ошибка при запросе к VK API. Код состояния: {response.status_code}')

        raise ValueError('Невозможно определить реальный ID.')

   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id}
       response = requests.get(url, params={**self.params, **params})
       return response.json()
   
   def filter_data_photo(self,responce):
        my_list = []
        self.responce = responce
        for i in responce['response']['items']:
            w = 0
            h = 0
            my_dict = {}
            for d in i['sizes']:
                if d['width'] > w and d['height'] > h:
                    h = d['height']
                    w = d['width']
                    
                    my_dict['file_name'] = str(i['likes']['count'])+'_' +str(i['date'])+'.jpg'
                    my_dict['size'] = d['type']
                    my_dict['url'] = d['url']
            my_list.append(my_dict)
        return my_list
       
   def photos_get(self,album_id = 'profile',count = 5):
       self.album_id = album_id
       self.count = count
       url = 'https://api.vk.com/method/photos.get'
       params = {'owner_id': self.id,
        'album_id': album_id,
        'extended' : 1,
		'count': count,
		'photo_sizes': 0,
        'rev' : 1
        }
    
       responce = requests.get(url, params={**self.params, **params})
       return responce.json()
   
class YandexDisk:
    url = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {'Authorization': f'OAuth {access_token}'}

    def create_folder(self,name_folder):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.access_token}'
        }
        params = {
            "path": "/" + name_folder, 
            "overwrite": "true"
                  }
        response = requests.put(self.url, headers=headers, params=params)
        if response.status_code == 201:
            print(f"Папка '{name_folder}' создана на Яндекc.Диск")
            
        elif response.status_code == 409:
            print(f"Папка '{name_folder}' уже есть на вашем Яндекc.Диске")
            
        else:
            print (response.status_code)
            print(response.text)
            
    def delete_folder(self,name_folder):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.access_token}'
        }
        params = {
            "path": "/" + name_folder, 
            "overwrite": "true"
                  }
        response = requests.delete(self.url, headers=headers, params=params)
        return 'Папка "{name_folder}" удалена с вашего Яндекс.Диска'
        
    def upload_photo_by_url(self,data_photos,folder_name = '' ):
        if folder_name == '':
            pass
        else:
            self.create_folder(folder_name)
        for file in tqdm(data_photos):
            file_name = file['file_name']
            url_photo = file['url']
            url = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path={folder_name}/{file_name}'
            headers = {
                    'Authorization': f'OAuth {self.access_token}'
                }       
            response = requests.get(url, headers=headers)
            data = response.json()
            if 'href' in data:
                upload_url = data['href']
                photo_data = requests.get(url_photo).content
                upload_response = requests.put(upload_url, data=photo_data)
                if upload_response.status_code == 201:
                    continue
                else:
                    print(f'Ошибка при загрузке фото. Код состояния: {upload_response.status_code}')
            else:
                print(f'Ошибка при получении URL для загрузки. Код состояния: {response.status_code}')
                print(data)
        print(f'Все фото загружены в папку "{folder_name}"')


def work(token_vk,yandex_token,users_id,name_folder = "",count = 5,vk_album = 'profile'):
    vk = VK(token_vk, users_id)  # создаем класс вк
    yandex = YandexDisk(yandex_token) # создаем класс яндекса
    data_photo = vk.photos_get(vk_album,count) # получаем список фотографий Можно указать альбом из которого будем скачивать и количество фотограффий
    filtered_data = vk.filter_data_photo(data_photo) #фильтруем выбирая самое большое разрешение и создаем список со словарями
    yandex.upload_photo_by_url(filtered_data,name_folder) #загружаем фотографии на яндекс диск можно указать имя папки

work(token_vk,token_yandex,users_id,"VK_photo")    

