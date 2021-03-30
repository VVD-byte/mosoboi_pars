import nest_asyncio
nest_asyncio.apply()
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import xlsxwriter


class Parser:
    def __init__(self, name, url):
        self.name = name
        self.url_pars = url
        self.dat = {}
        self.field = set()

    @staticmethod
    async def get(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def pars(self):
        print(f'start {self.name}')
        url = f'https://www.mosoboi.ru{self.url_pars}?list_by=92&PAGEN_2=1'
        a = requests.get(url)
        soup = BeautifulSoup(a.text, 'lxml')
        dat = soup.find_all('a', {'class': 'pagenav p26'})
        if dat:
            loop = asyncio.get_event_loop()
            coroutines = [self.get(f'https://www.mosoboi.ru{self.url_pars}?list_by=92&PAGEN_2={i}') for i in range(1, int(dat[-1].getText()) + 1)]
            results = loop.run_until_complete(asyncio.gather(*coroutines))
        else:
            results = [a.text]
        return await asyncio.coroutine(self.get_dat)(results)

    def get_dat(self, results):
        for i in results:
            soup = BeautifulSoup(i, 'lxml')
            for j in soup.find_all('div', {'class': 'col-xs-3'}):
                name = j.find('div', {'class', 'product-item__fabric-name'}).getText().replace('  ', '').replace('\n', '')
                self.dat[name] = {}
                self.dat[name]['Имя'] = name
                for q in j.find('ul', {'itemprop': 'description'}).find_all('li'):
                    text = q.getText().replace("  ", "").replace('\n', '')
                    self.dat[name][f'{text.split(":")[0]}'] = text.split(":")[1]
                self.dat[name]['url'] = j.find('div', {'class', 'product-item__hover'}).find('a', href=True)
                if self.dat[name]['url']: self.dat[name]['url'] = 'https://www.mosoboi.ru' + self.dat[name]['url'].get('href')
                try:
                    self.dat[name]['Изображение'] = 'https://www.mosoboi.ru' + j.find('div', {'class': 'product-item__image'}).find('img').get('src')
                    self.dat[name]['Новая цена'] = j.find('div', {'class': 'new_price'}).getText().replace(' ', '').replace('\n', '').replace('₽', '')
                    self.dat[name]['Старая цена'] = j.find('div', {'class': 'old-price'}).getText().replace(' ', '').replace('\n', '').replace('₽', '')
                    self.dat[name]['Скидка'] = int(self.dat[name]['Старая цена']) - int(self.dat[name]['Новая цена'])
                except:
                    pass
                for _ in self.dat[name].keys():
                    self.field.add(_)
        print(len(self.dat))
        try:
            workbook = xlsxwriter.Workbook(f'{self.name}.xlsx')
            worksheet = workbook.add_worksheet()
            for id_, i in enumerate(self.field):
                worksheet.write(0, id_, i)
            for id_, i in enumerate(self.dat):
                for _id, j in enumerate(self.field):
                    worksheet.write(id_ + 1, _id, self.dat[i].get(j, '-'))
            workbook.close()
        except:
            return False
        return True


if __name__ == '__main__':
    import json
    with open('dat.json') as t:
        dat = json.loads(t.read())
    for i in dat:
        a = Parser(i, dat[i])
        a.pars()
