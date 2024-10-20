TODO PingRequest est envoyé a des moment clé, voir comparaison quand click

TODO => utiliser SQLite plutot que tinyDB pour HumanTiming
TODO => "Planning de bot" => 12 heures max par jour puis remplacer par un autre bot
le tout avec proxy mobile pour que l'ip soit reset régulièrement

json par session (avec date heure debut dans nom de fichier)

contient liste de :

- date heure
- Message avec ses données

Pour que l'objectif soit -> get_human_timing(MessageDavant(jeveuxqueparam1=3), MessageDapres()) (on met sa en cache)
on récupère tout les delta de temps entre ces 2 messages avec leur paramètre spécifique

puis Ditribution paramétrique (log normale) OU Empirical CDF (se renseigner) pour obtenir un temps human like qu'on choisis au hasard

Avantages :
-> Contrer l'antibot (en ce qui concerne les timings) qui est surement basé sur du machine learning
-> Ne pas devoir choisir des ranges de temps d'attente écris en dur dans le code mais plutot basé sur des données humaines
