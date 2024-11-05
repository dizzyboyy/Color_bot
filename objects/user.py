class User():
    name = ''
    surname = ''
    patronymic = ''
    chat_id = ''
    username = ''
    date = ''
    access = ''
    is_wait_access = ''
    root = ''
    is_company=''
    company_name=''
    company_link=''
    phone=''

    def __init__(self, data):
        self.name = data['name']
        self.surname = data['surname']
        self.patronymic = data['patronymic']
        self.date = data['date']
        self.access = data['access']
        self.username = data['username']
        self.is_wait_access = data['is_wait_access']
        self.root = data['root']
        self.is_company = data['is_company']
        self.company_name = data['company_name']
        self.company_link = data['company_link']
        self.phone = data['phone']
