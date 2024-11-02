File "C:\Users\Valentin\Documents\Workspace\Bot-DofusUnity\.venv\Lib\site-packages\ankama_launcher_emulator\haapi\haapi.py", line 41, in signOnWithApiKey
response = self.zaap_session.post(url, json={"game": game_id})
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\Valentin\Documents\Workspace\Bot-DofusUnity\.venv\Lib\site-packages\requests\sessions.py", line 637, in post
return self.request("POST", url, data=data, json=json, **kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\Valentin\Documents\Workspace\Bot-DofusUnity\.venv\Lib\site-packages\requests\sessions.py", line 589, in request
resp = self.send(prep, **send_kwargs)

- TODO Quand ca fail au lancement a cause de la co ou autre, ca ne kill pas la fenetre

- TODO Gérer les sac de ressources pas correctement vidé

- Plus de données pour human timings

- Trouver un proxy avec ip rotatif avec prix ok
