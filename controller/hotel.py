#Controller da API
from flask_restful import Resource, reqparse
from model.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

path_param = reqparse.RequestParser()
path_param.add_argument('hotel_id', type=str)
path_param.add_argument('nome', type=str)


def nomalize_path_params(hotel_id=None,
                         nome=None,
                         **dados):

    if nome:
        return {'nome': nome}
    
    else:
        return{'message': 'Incorrect consult'}

class Hoteis(Resource):

    def get(self):

        cursor = sqlite3.connect('banco.db').cursor()

        dados = path_param.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = nomalize_path_params(**dados_validos)

        if parametros.get('nome'):
            consulta = "SELECT * FROM hoteis \
                        WHERE nome = ?"
            
            tupla = tuple([parametros[chave] for chave in parametros])
            print(tupla)
            resultado = cursor.execute(consulta, tupla)
        
        else:

            consulta = "select * from hoteis"
            resultado = cursor.execute(consulta)

        lista_json = []
        for linha in resultado:
            lista_json.append({'hotel_id': linha[0],
                               'nome': linha[1]})

        return {'result': lista_json}

class Hotel(Resource):

    argumentos = reqparse.RequestParser()
    argumentos.add_argument('hotel_id', type=str, required=True, help="Não pode ser nulo o id")
    argumentos.add_argument('nome', type=str, required=True, help="Não pode ser nulo o nome")

    def get(self, hotel_id):
        
        hotel = HotelModel.find_hotel(hotel_id)
        
        if hotel:
            return hotel.json()

        return {"message": "Hotel not found"}, 404

    @jwt_required
    def post(self, hotel_id):

        if HotelModel.find_hotel(hotel_id):
            return {"message": "hotel_id '{}' already exists".format(hotel_id)}, 400

        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(**dados)

        try:
            hotel.save_hotel()

        except:
            return {"message": "error"}, 500

        return hotel.json()

    @jwt_required
    def put(self, hotel_id):
    
        dados = Hotel.argumentos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)

        if hotel_encontrado:
            hotel_encontrado.update_hotel(dados['nome'])
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200

        hotel = HotelModel(**dados)

        try:
            hotel.save_hotel()
        
        except:
            return {"message": "error"}, 500

        return hotel.json(), 201

    @jwt_required
    def delete(self, hotel_id):
        
        hotel = HotelModel.find_hotel(hotel_id)

        if hotel:
            try:
                hotel.delete_hotel()   

            except:
                return {"message": "error"}, 500
                
            return {"message": "hotel deleted"}

        return {"message": "hotel not found "}

