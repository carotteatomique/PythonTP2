
import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler:

    def __init__(self):
        self.__reservations = {}
        self.__utilisateurs = {}
        self.__chalets = {}

    @property
    def reservations(self):
        return self.__reservations

    def post_reservations(self, reservations, nouv_reservation):
        if reservations not in self.__reservations:
            raise ValueError('Réservation inexistante')
        if nouv_reservation in self.__reservations[reservations]:
            raise ValueError('Réservation déjà existante')
        index = self.__reservations[reservations].index(reservations)
        self.__reservations[reservations][index] = nouv_reservation

    def put_reservations(self, nouv_reservation, anc_reservation):
        if nouv_reservation == anc_reservation:
            raise ValueError('Aucun changement dans la reservation')
        for reservations, reservations_list in self.__reservations.items():
            if anc_reservation in reservations_list:
                index = reservations_list.index(anc_reservation)
                reservations_list[index] = nouv_reservation
                break
        else:
            raise ValueError('Réservation inexistante')

    def get_reservation(self, ID_reservation):
        for reservations, reservations_list in self.__reservations.items():
            if ID_reservation in reservations_list:
                return reservations_list[0]
        raise ValueError('ID inexistant')

    def get_reservations(self, email):
        if email in self.__reservations:
            return self.__reservations[email]
        raise ValueError('Email inexistant')

    def post_utilisateur(self, reservations, utilisateur):
        if reservations not in self.__utilisateurs:
            self.__utilisateurs[reservations] = []
        if utilisateur in self.__utilisateurs[reservations]:
            raise ValueError('Utilisateur déjà existant')
        self.__utilisateurs[reservations].append(utilisateur)

    def post_chalet(self, chalets, chalet):
        if chalets not in self.__chalets:
            self.__chalets[chalets] = []
        if chalet in self.__chalets[chalets]:
            raise ValueError('Chalet déjà existant')
        self.__chalets[chalets].append(chalet)

    def get_chalet(self, ID_chalet):
        for chalets, chalets_list in self.__chalets.items():
            if ID_chalet in chalets_list:
                return chalets_list[0]
        raise ValueError('ID de chalet inexistant')

    def post_chalet_reservation(self, reservations, ID_chalet, plage):
        if reservations in self.__reservations:
            if ID_chalet in self.__reservations[reservations]:
                self.__reservations[reservations][ID_chalet].append(plage)
            else:
                raise ValueError('ID de chalet inexistant')
        else:
            raise ValueError('Réservation inexistante')


class TPBaseHTTPRequestHandler(BaseHTTPRequestHandler):

    handler = Handler()
    # Permet la gestion de toutes les requetes de type get
    def do_GET(self):
        path = self.path
        print(path)

        if path.startswith('/reservation/'):
            reservation = path.split('/')[2]
            content = 'Reservation: ' + reservation + ' -> ' + str(self.handler.get_reservation(reservation))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(content, 'utf-8'))

        elif path.startswith('/reservations/'):
            reservations = path.split('/')[2]
            content = 'Reservations: ' + reservations + ' -> ' + str(self.handler.get_reservations(reservations))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end
class ServeurTest:

    # Méthode pour initialiser le serveur et le garder en marche
    @staticmethod
    def run(serveur_class=HTTPServer, serveur_port=8000, handler_class=TPBaseHTTPRequestHandler):
        # le serveur va écouter sur localhost sur le port passé en paramètre
        serveur_adresse = ('localhost', serveur_port)
        # Les requêtes vont être gérées par handler_class passé en paramètre (notre class TPBaseHTTPRequestHandler
        # par défaut)
        httpd = serveur_class(serveur_adresse, handler_class)
        # Écoute pour des requêtes jusqu'à ce qu'on arrête le serveur
        httpd.serve_forever()

import unittest


#Test unitaires

class TestHandler(unittest.TestCase):

    def setUp(self):
        self.handler = Handler()

    def test_post_reservations(self):
        self.handler.post_reservations("John", "Reservation 1")
        self.assertEqual(self.handler.reservations["John"], ["Reservation 1"])

    def test_post_reservations_existing(self):
        self.handler.reservations = {"John": ["Reservation 1"]}
        with self.assertRaises(ValueError):
            self.handler.post_reservations("John", "Reservation 1")

    def test_put_reservations(self):
        self.handler.reservations = {"John": ["Reservation 1"]}
        self.handler.put_reservations("Reservation 2", "Reservation 1")
        self.assertEqual(self.handler.reservations["John"], ["Reservation 2"])

    def test_put_reservations_no_change(self):
        self.handler.reservations = {"John": ["Reservation 1"]}
        with self.assertRaises(ValueError):
            self.handler.put_reservations("Reservation 1", "Reservation 1")

    def test_get_reservation(self):
        self.handler.reservations = {"John": ["Reservation 1"]}
        reservation = self.handler.get_reservation("Reservation 1")
        self.assertEqual(reservation, "Reservation 1")

    def test_get_reservation_nonexistent(self):
        self.handler.reservations = {"John": ["Reservation 1"]}
        with self.assertRaises(ValueError):
            self.handler.get_reservation("Reservation 2")

    def test_get_reservations(self):
        self.handler.reservations = {"john@example.com": ["Reservation 1", "Reservation 2"]}
        reservations = self.handler.get_reservations("john@example.com")
        self.assertEqual(reservations, ["Reservation 1", "Reservation 2"])

    def test_get_reservations_nonexistent(self):
        self.handler.reservations = {"john@example.com": ["Reservation 1", "Reservation 2"]}
        with self.assertRaises(ValueError):
            self.handler.get_reservations("jane@example.com")

    def test_post_utilisateur(self):
        self.handler.post_utilisateur("Reservation 1", "John")
        self.assertEqual(self.handler.utilisateurs["Reservation 1"], ["John"])

    def test_post_utilisateur_existing(self):
        self.handler.utilisateurs = {"Reservation 1": ["John"]}
        with self.assertRaises(ValueError):
            self.handler.post_utilisateur("Reservation 1", "John")

    def test_post_chalet(self):
        self.handler.post_chalet("Resort A", "Chalet 1")
        self.assertEqual(self.handler.chalets["Resort A"], ["Chalet 1"])

    def test_post_chalet_existing(self):
        self.handler.chalets = {"Resort A": ["Chalet 1"]}
        with self.assertRaises(ValueError):
            self.handler.post_chalet("Resort A", "Chalet 1")

    def test_get_chalet(self):
        self.handler.chalets = {"Resort A": ["Chalet 1"]}
        chalet = self.handler.get_chalet("Chalet 1")
        self.assertEqual(chalet, "Chalet 1")

    def test_get_chalet_nonexistent(self):
        self.handler.chalets = {"Resort A": ["Chalet 1"]}
        with self.assertRaises(ValueError):
            self.handler.get_chalet("Chalet 2")

