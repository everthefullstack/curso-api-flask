#Controller da API
from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import safe_str_cmp

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="Não pode ficar em branco")
atributos.add_argument('senha', type=str, required=True, help="Não pode ficar em branco")

class User(Resource):

    def get(self, user_id):
        
        user = UserModel.find_user(user_id)
        
        if user:
            return user.json()

        return {"message": "User not found"}, 404

    @jwt_required
    def delete(self, user_id):
        
        user = UserModel.find_user(user_id)

        if user:
            user.delete_user()   
                
            return {"message": "User deleted"}

        return {"message": "User not found"}

class UserRegister(Resource):

    def post(self):

        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {"message": "Login '{}' already exists".format(dados['login'])}

        user = UserModel(**dados)
        user.save_user()
        return {"message": "User created successfully"}, 201

class UserLogin(Resource):

    def post(cls):
        dados = atributos.parse_args()
        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):

            token = create_access_token(identity=user.user_id)
            return {"acess_token": token}, 200
        
        return {"message": "User or password is incorrect"}, 401