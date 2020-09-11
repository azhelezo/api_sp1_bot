import os
import requests
import telegram
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename='running.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s'
    )


PRACTICUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/?'
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    if (
            ('homework_name' or 'status') not in homework or
            (homework['status'] not in ['rejected', 'approved'])
        ):
        logging.info(f'Error in response: {homework}')
        return 'Error in response'
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    logging.info(f'homework_name = "{homework_name}", verdict = "{verdict}"')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            PRACTICUM_URL,
            params={
                'from_date': current_timestamp
                             if current_timestamp != None else 0
                },
            headers=headers
            )
    except Exception as ex:
        logging.error(f'Status check error: {ex}')
        send_message('Status check error')
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    send_message('Running')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            logging.error(f'Bot returned error: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
