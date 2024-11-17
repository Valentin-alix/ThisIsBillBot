# Behavior Testing Framework

Framework pour tester les behaviors en mockant l'EventManager et en simulant les messages serveur.

## Architecture

### BehaviorTestBase

Classe de base qui fournit :

- **Bot fake** : Un bot complet mais isolé (`is_fake=True`)
- **Message interception** : Capture tous les messages envoyés par la behavior via `event_manager.send()`
- **Message injection** : Simule des messages du serveur via `inject_server_message()`
- **Callback tracking** : Suivi automatique des callbacks de behavior
- **Assertions helpers** : Méthodes utilitaires pour vérifier les résultats

### Méthodes principales

#### Setup et configuration

```python
def setUp(self):
    # Appelé automatiquement, initialise :
    # - self.bot
    # - self.game_state
    # - self.event_manager
    # - self.sent_messages (liste des messages envoyés)
```

#### Démarrage de behavior

```python
self.start_behavior(
    behavior,
    callback=None,  # None = callback auto-généré
    parent=None,
    *args,
    **kwargs
)
```

#### Injection de messages serveur

```python
# Simuler un message du serveur
server_msg = SomeProtobufMessage(...)
self.inject_server_message(server_msg)
```

#### Assertions

```python
# Vérifier qu'un message a été envoyé
self.assert_message_sent(MessageType, count=1)

# Récupérer tous les messages envoyés d'un type (avec typage générique)
messages: list[MessageType] = self.get_sent_messages(MessageType)

# Récupérer un message spécifique (avec typage générique)
msg: MessageType = self.get_sent_message(MessageType, index=0)  # index=0 par défaut

# Attendre le callback
assert self.wait_for_callback(timeout=1.0)

# Vérifier le succès
self.assert_callback_success()

# Vérifier une erreur
self.assert_callback_error("ERROR_CODE")

# Nettoyer les messages
self.clear_sent_messages()
```

## Exemples d'utilisation

### Test simple : behavior qui envoie un message

```python
class TestChatBehavior(BehaviorTestBase):
    def test_send_message(self):
        behavior = ChatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            logger=self.bot.logger,
        )

        # Démarrer
        self.start_behavior(behavior, content="Hello")

        # Attendre la fin
        assert self.wait_for_callback(timeout=1.0)

        # Vérifier
        self.assert_callback_success()
        self.assert_message_sent(ChatChannelMessageRequest, count=1)

        # Le typage est automatiquement inféré !
        msg = self.get_sent_message(ChatChannelMessageRequest)
        assert msg.content == "Hello"  # PyLance reconnaît msg.content
```

### Test avec réponse serveur

```python
def test_wait_for_server_response(self):
    behavior = SomeBehavior(...)

    # Démarrer
    self.start_behavior(behavior)

    # Vérifier que la requête est envoyée
    self.assert_message_sent(RequestMessage, count=1)

    # Behavior doit attendre
    assert behavior.is_running.is_set()
    assert not self.callback_called.is_set()

    # Simuler réponse serveur
    response = ResponseMessage(...)
    self.inject_server_message(response)

    # Vérifier que la behavior réagit
    assert self.wait_for_callback(timeout=1.0)
    self.assert_callback_success()
```

### Test avec behavior parent/enfant

```python
def test_parent_child_behavior(self):
    parent = ParentBehavior(...)
    child = ChildBehavior(...)

    # Démarrer parent
    self.start_behavior(parent)

    # Démarrer enfant avec parent
    self.start_behavior(child, parent=parent)

    # Stopper parent devrait stopper l'enfant
    parent.stop()

    assert not parent.is_running.is_set()
    assert not child.is_running.is_set()
```

### Test avec timers

```python
def test_behavior_with_timer(self):
    behavior = DelayedBehavior(...)

    self.start_behavior(behavior)

    # Ne devrait pas finir immédiatement
    assert not self.wait_for_callback(timeout=0.1)

    # Devrait finir après le délai
    assert self.wait_for_callback(timeout=2.0)
    self.assert_callback_success()
```

### Test de gestion d'erreur

```python
def test_behavior_error_handling(self):
    behavior = SomeBehavior(...)

    self.start_behavior(behavior)

    # Simuler un message d'erreur du serveur
    error_msg = ErrorMessage(code=404)
    self.inject_server_message(error_msg)

    # Vérifier que la behavior fail correctement
    assert self.wait_for_callback(timeout=1.0)
    self.assert_callback_error("RESOURCE_NOT_FOUND")
```

### Test de cleanup

```python
def test_behavior_cleanup(self):
    behavior = SomeBehavior(...)

    self.start_behavior(behavior)

    # Vérifier qu'elle a enregistré des listeners
    initial_count = len(self.event_manager.listeners_by_type_msg.get(SomeMessage, []))
    assert initial_count > 0

    # Stopper
    behavior.stop()

    # Vérifier le cleanup
    final_count = len(self.event_manager.listeners_by_type_msg.get(SomeMessage, []))
    assert final_count < initial_count
    assert not behavior.is_running.is_set()
```

## Tester des behaviors complexes

Pour les behaviors avec beaucoup de dépendances (comme `FightBehavior`), utilisez des mocks pour simplifier :

```python
class TestComplexBehavior(BehaviorTestBase):
    def setUp(self):
        super().setUp()

        # Mock les dépendances complexes
        self.dependency1 = MagicMock(spec=SomeDependency)
        self.dependency2 = MagicMock(spec=AnotherDependency)

    def test_behavior_lifecycle(self):
        behavior = ComplexBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            logger=self.bot.logger,
            dependency1=self.dependency1,
            dependency2=self.dependency2,
        )

        self.start_behavior(behavior)

        # Vérifier que les listeners sont enregistrés
        listeners = self.event_manager.listeners_by_type_msg.get(SomeEvent, [])
        assert len(listeners) > 0

        # Simuler un événement
        self.inject_server_message(SomeEvent())

        # Vérifier que les dépendances ont été utilisées
        self.dependency1.some_method.assert_called()
```

### Tester les behaviors parent/enfant

```python
def test_parent_stops_children(self):
    # Mock le child behavior
    mock_child = MagicMock(spec=ChildBehavior)

    parent = ParentBehavior(
        event_manager=self.event_manager,
        game_state=self.game_state,
        logger=self.bot.logger,
        child_behavior=mock_child,
    )

    self.start_behavior(parent)

    # Vérifier que le child a été démarré
    mock_child.start.assert_called()

    # Stopper le parent
    parent.stop()

    # Le child doit aussi être stoppé
    mock_child.stop.assert_called()
```

## Patterns avancés

### Mock de services externes

```python
def test_with_external_service(self):
    # Mock d'un service IA par exemple
    with patch('src.services.ai.human_solo_talk.HumanSoloTalk') as mock_ai:
        mock_ai.return_value.get_solo_human_talk_in_general_msg.return_value = "Mocked message"

        behavior = ChatBehavior(...)
        self.start_behavior(behavior, content=None)  # None = utilise l'IA

        # Vérifier que l'IA a été appelée
        mock_ai.return_value.get_solo_human_talk_in_general_msg.assert_called_once()
```

### Scénarios complexes multi-étapes

```python
def test_complex_scenario(self):
    behavior = ComplexBehavior(...)

    self.start_behavior(behavior)

    # Étape 1 : Vérifier première action
    self.assert_message_sent(FirstRequest, count=1)
    self.clear_sent_messages()

    # Simuler réponse étape 1
    self.inject_server_message(FirstResponse(...))

    # Étape 2 : Vérifier deuxième action
    self.assert_message_sent(SecondRequest, count=1)

    # Simuler réponse étape 2
    self.inject_server_message(SecondResponse(...))

    # Vérifier la fin
    assert self.wait_for_callback(timeout=1.0)
    self.assert_callback_success()
```

## Exécution des tests

```bash
# Tous les tests de behaviors
poetry run python -m unittest discover tests/test_behaviors

# Un test spécifique
poetry run python -m unittest tests.test_behaviors.test_chat_behavior

# Une classe de test
poetry run python -m unittest tests.test_behaviors.test_chat_behavior.TestChatBehavior

# Un test précis
poetry run python -m unittest tests.test_behaviors.test_chat_behavior.TestChatBehavior.test_send_custom_message
```

## Typage générique

Le framework utilise des TypeVars pour fournir un typage correct automatiquement :

```python
# ✅ GOOD - PyLance reconnaît automatiquement le type
msg = self.get_sent_message(ChatChannelMessageRequest)
msg.content  # PyLance sait que c'est ChatChannelMessageRequest et propose l'autocomplete

messages = self.get_sent_messages(ChatChannelMessageRequest)
messages[0].content  # PyLance sait que c'est list[ChatChannelMessageRequest]

# ❌ BAD - Pas de typage
msg = self.sent_messages[0]  # PyLance sait seulement que c'est Message
msg.content  # Pas d'autocomplete, pas de type checking
```

Les méthodes `get_sent_message()` et `get_sent_messages()` utilisent un TypeVar générique qui garantit que le type de retour correspond au type passé en paramètre.

## Bonnes pratiques

1. **Un test = un scénario** : Chaque test doit tester un seul comportement ou cas d'usage
2. **Cleanup automatique** : Le `tearDown` s'occupe du cleanup, pas besoin de le faire manuellement
3. **Timeouts raisonnables** : Utilisez des timeouts courts (0.1-1s) pour les tests rapides
4. **Messages clairs** : Utilisez des assertions avec des messages explicites
5. **Isolation** : Chaque test doit être indépendant (pas de state partagé)
6. **Mock minimal** : Ne mocker que ce qui est nécessaire, le reste utilise le vrai code
7. **Typage générique** : Utilisez `get_sent_message()` plutôt que d'accéder directement à `sent_messages[0]` pour bénéficier du typage
