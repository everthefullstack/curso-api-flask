#Controller da API
from flask_restful import Resource, reqparse
from model.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST
import traceback

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="Não pode ficar em branco")
atributos.add_argument('senha', type=str, required=True, help="Não pode ficar em branco")
atributos.add_argument('email', type=str)
atributos.add_argument('ativado', type=bool)

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
        if not dados.get('email') or dados.get('email') is None:
                return {'message': 'The field e-mail cannot be left blank.'}, 400

        if UserModel.find_by_email(dados['email']):
            return {'message': 'Email already exists.'}, 400

        if UserModel.find_by_login(dados['login']):
            return {"message": "Login '{}' already exists".format(dados['login'])}

        user = UserModel(**dados)
        user.ativado = False

        try:
            user.save_user()
            user.send_email_confirmation()
        
        except:
            user.delete_user()
            traceback.print_exc()
            return{'message': 'Internal error as ocurred.'}, 500

        return {"message": "User created successfully"}, 201

class UserLogin(Resource):

    def post(cls):
        dados = atributos.parse_args()
        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):

            if user.ativado:
                token = create_access_token(identity=user.user_id)
                return {"acess_token": token}, 200

            return{'message': 'User not confirmed.'}
        return {"message": "User or password is incorrect"}, 401

class UserLogout(Resource):

    @jwt_required
    def post(self):

        jwt_id = get_raw_jwt()['jti']#json token identifier
        BLACKLIST.add(jwt_id)

        return {'message': 'Logged out successfully'}, 200

class UserConfirm(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_user(user_id)
    
        if not user:
            return{"message": "User not found"}
        
        user.ativado = True
        user.save_user()

        return{"message": "user id confirmed successfully"}
