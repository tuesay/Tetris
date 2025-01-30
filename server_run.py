from network.battle_server import BattleServer

if __name__ == "__main__":
    server = BattleServer(host="127.0.0.1", port=5555)
    server.start()