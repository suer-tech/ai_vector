import json

import requests
import numpy as np
import faiss


def interact_stream(user_id, data, voiceflow_api_key, project_id):
    data_text = {
        "action": {
            "type": "text",
            'payload': f'{data}'
        }
    }

    url = f"https://general-runtime.voiceflow.com/v2/project/{project_id}/user/{user_id}/interact/stream"

    headers = {
        'Accept': 'text/event-stream',
        'Authorization': voiceflow_api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=data_text, stream=True)
    print(response.text)

    if response.status_code == 200:
        # Обработка данных ответа
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    try:
                        parsed_data = json.loads(decoded_line[6:])  # Удаляем "data:" и парсим JSON

                        # Извлечение эмбеддингов из ответа
                        output_embedding = parsed_data['paths'][0]['event']['payload']['message']
                        embedding_list = json.loads(output_embedding)
                        return embedding_list
                    except json.JSONDecodeError:
                        print(f"Не удалось разобрать: {decoded_line}")
                    except KeyError:
                        print(f"Нет ответа: {decoded_line}")
    else:
        print(f"Error: {response.status_code}")


def generate_embedding(text):
    # Здесь должен быть код для отправки текста на API модели генерации эмбеддингов
    response = interact_stream(user_id="your_user_id_here", data=text,voiceflow_api_key="VF.DM.67499102b357d4928b4ac58b.ZQrIJbkjPUwhCr2I", project_id="672caaaf565396bb1012956f")  # Пример user_id
    return response


def search_instruction(query):
    query_embedding = generate_embedding(query)  # Генерация эмбеддинга для запроса
    distances, indices = index.search(np.array([query_embedding]), k=3)  # Поиск ближайших соседей
    results = [instructions_dict[i] for i in indices[0]]
    return results


def process_user_question(question):
    query_embedding = generate_embedding(question)

    # Поиск по векторной базе данных
    found_instruction = search_instruction(query_embedding)

    # Генерация ответа на основе найденной инструкции
    answer_data = {"question": question, "instruction": found_instruction}

    answer_response = interact_stream(user_id="user_123", data=answer_data, voiceflow_api_key="VF.DM.67499102b357d4928b4ac58b.ZQrIJbkjPUwhCr2I", project_id="672caaaf565396bb1012956f")

    return answer_response['answer']  # Предполагаем, что API возвращает ответ