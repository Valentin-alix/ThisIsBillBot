# Examples de tests de behaviors

Ce document présente des exemples concrets de tests pour différents types de behaviors.

## 1. Behavior simple (ChatBehavior)

**Cas d'usage** : Behavior qui envoie un message et se termine immédiatement.

```python
def test_send_custom_message(self):
    behavior = ChatBehavior(
        event_manager=self.event_manager,
        game_state=self.game_state,
        logger=self.bot.logger,
    )

    # Démarrer avec paramètres
    self.start_behavior(behavior, content="Hello World!", channel=Channel.GLOBAL)

    # Attendre la fin
    assert self.wait_for_callback(timeout=1.0)
    self.assert_callback_success()

    # Vérifier le message envoyé (avec typage automatique)
    msg = self.get_sent_message(ChatChannelMessageRequest)
    assert msg.content == "Hello World!"
    assert msg.channel == Channel.GLOBAL
```

**Ce qu'on teste** :
- ✅ Le message est envoyé
- ✅ Le callback est appelé
- ✅ Le contenu du message est correct
- ✅ La behavior se termine correctement

## 2. Behavior avec réponse serveur

**Cas d'usage** : Behavior qui attend une réponse du serveur avant de continuer.

```python
def test_behavior_waits_for_server_response(self):
    behavior = WaitForChatResponseBehavior(...)

    self.start_behavior(behavior, message="Hello")

    # Vérifier que la requête est envoyée
    self.assert_message_sent(ChatChannelMessageRequest, count=1)

    # La behavior doit attendre
    assert behavior.is_running.is_set()
    assert not self.callback_called.is_set()

    # Simuler la réponse du serveur
    server_response = ChatChannelMessageEvent(
        content="Hello back!",
        sender_name="Server",
        channel=Channel.GLOBAL,
    )
    self.inject_server_message(server_response)

    # Maintenant la behavior doit finir
    assert self.wait_for_callback(timeout=1.0)
    self.assert_callback_success()
```

**Ce qu'on teste** :
- ✅ La requête est envoyée
- ✅ La behavior attend la réponse
- ✅ La behavior réagit à la réponse serveur
- ✅ La behavior finit correctement après la réponse

## 3. Behavior complexe (FightBehavior)

**Cas d'usage** : Behavior avec lifecycle complexe, multiples événements et child behaviors.

```python
class TestFightBehaviorSimple(BehaviorTestBase):
    def setUp(self):
        super().setUp()

        # Mock toutes les dépendances complexes
        self.path_finding = MagicMock(spec=Pathfinding)
        self.fight_turn_behavior = MagicMock(spec=FightTurnBehavior)
        self.fight_preparation_behavior = MagicMock(spec=FightPreparationBehavior)
        # ...

    def test_fight_behavior_finishes_when_leaving_map(self):
        behavior = FightBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            logger=self.bot.logger,
            path_finding=self.path_finding,
            fight_turn_behavior=self.fight_turn_behavior,
            fight_preparation_behavior=self.fight_preparation_behavior,
            # ...
        )

        self.start_behavior(behavior)

        # Simuler la sortie du combat
        map_event = MapComplementaryInformationEvent()
        self.inject_server_message(map_event)

        # La behavior doit finir
        assert self.wait_for_callback(timeout=1.0)
        self.assert_callback_success()
```

**Ce qu'on teste** :
- ✅ La behavior démarre correctement
- ✅ Les listeners sont enregistrés
- ✅ La behavior réagit aux événements
- ✅ La behavior finit dans les bonnes conditions
- ✅ Le cleanup est fait correctement

**Stratégie** : On mock les dépendances complexes et on se concentre sur le comportement message-driven.

## 4. Test du cleanup des listeners

```python
def test_fight_behavior_cleanup_removes_listeners(self):
    behavior = FightBehavior(...)

    self.start_behavior(behavior)

    # Compter les listeners
    listeners_count = len(
        self.event_manager.listeners_by_type_msg.get(
            MapComplementaryInformationEvent, []
        )
    )
    assert listeners_count > 0

    # Stopper
    behavior.stop()

    # Les listeners doivent être nettoyés
    final_count = len(
        self.event_manager.listeners_by_type_msg.get(
            MapComplementaryInformationEvent, []
        )
    )
    assert final_count < listeners_count
```

**Ce qu'on teste** :
- ✅ Les listeners sont enregistrés au démarrage
- ✅ Les listeners sont supprimés à l'arrêt
- ✅ Pas de fuite mémoire

## 5. Test avec multiples événements

```python
def test_fight_behavior_multiple_turn_events(self):
    behavior = FightBehavior(...)

    self.game_state.fight._is_map_fight_initialized = True
    self.start_behavior(behavior)

    # Envoyer plusieurs événements de tour
    for i in range(3):
        turn_event = FightTurnStartPlayingEvent()
        self.inject_server_message(turn_event)

    # La behavior doit rester active
    assert behavior.is_running.is_set()

    # Terminer le combat
    map_event = MapComplementaryInformationEvent()
    self.inject_server_message(map_event)

    assert self.wait_for_callback(timeout=1.0)
```

**Ce qu'on teste** :
- ✅ La behavior gère plusieurs événements successifs
- ✅ La behavior reste stable durant le combat
- ✅ La behavior finit au bon moment

## 6. Test de typage générique

```python
def test_typing_with_get_sent_message(self):
    behavior = ChatBehavior(...)

    self.start_behavior(behavior, content="Hello World!")
    assert self.wait_for_callback(timeout=1.0)

    # PyLance infère automatiquement le type ChatChannelMessageRequest
    msg = self.get_sent_message(ChatChannelMessageRequest)

    # Autocomplete et type checking fonctionnent ici ✅
    assert msg.content == "Hello World!"
    assert msg.channel == Channel.GLOBAL
```

**Ce qu'on teste** :
- ✅ Le typage est correct
- ✅ L'IDE propose l'autocomplete
- ✅ Les erreurs de type sont détectées

## Bonnes pratiques résumées

### ✅ À FAIRE

1. **Mock les dépendances complexes** - Utiliser `MagicMock(spec=...)` pour les dépendances
2. **Tester le comportement, pas l'implémentation** - Se concentrer sur les messages et le lifecycle
3. **Utiliser le typage générique** - `get_sent_message()` au lieu de `sent_messages[0]`
4. **Tester le cleanup** - Vérifier que les listeners sont supprimés
5. **Un test = un scénario** - Chaque test doit être indépendant

### ❌ À ÉVITER

1. **Tester l'implémentation interne** - Ne pas tester les détails d'implémentation
2. **Dépendances réelles complexes** - Ne pas initialiser toute la chaîne de dépendances
3. **Tests dépendants** - Chaque test doit être isolé
4. **Timeouts trop longs** - Utiliser des timeouts courts (0.1-1s)
5. **Accès direct à sent_messages** - Utiliser les helpers avec typage

## Structure type d'un test

```python
class TestMyBehavior(BehaviorTestBase):
    def setUp(self):
        super().setUp()
        # Mock les dépendances
        self.dependency = MagicMock(spec=SomeDependency)

    def test_specific_scenario(self):
        # 1. ARRANGE - Créer la behavior
        behavior = MyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            logger=self.bot.logger,
            dependency=self.dependency,
        )

        # 2. ACT - Démarrer et simuler des événements
        self.start_behavior(behavior, param="value")
        self.inject_server_message(SomeEvent())

        # 3. ASSERT - Vérifier le comportement
        assert self.wait_for_callback(timeout=1.0)
        self.assert_callback_success()
        msg = self.get_sent_message(SomeRequest)
        assert msg.field == "expected_value"
```

## Résumé des tests disponibles

- **test_chat_behavior.py** - Behavior simple qui envoie un message
- **test_behavior_with_server_response.py** - Behavior qui attend une réponse serveur
- **test_fight_behavior_simple.py** - Behavior complexe avec lifecycle avancé
- **test_typing_example.py** - Démonstration du typage générique

**Total : 13 tests ✅**
