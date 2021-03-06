from deeppavlov.core.models.component import Component
from deeppavlov.core.common.log import get_logger
from state_utils import is_terminal_state

logger = get_logger(__name__)


class IntentFilter(Component):
    def __init__(self, intents, clf, default_intent=0, always_open=[], *args, **kwargs):
        self.intents = intents
        self.size = len(intents)
        self.clf = clf
        self.default_intent = default_intent
        self.max_batch_size = 128
        self.intent_idxs = [default_intent]*self.max_batch_size
        self.always_open = always_open

    def __call__(self, agent, utterances, batch_history):
        result = [[False] * self.size] * len(utterances)
        intents, scores, _ = self.clf(utterances)
        logger.debug(f"Intent from classifier: {intents}")
        states = agent.states
        for i in range(len(utterances)):
            skills_state = states[i]
            logger.debug(f"State: {skills_state}")
            for j, s in enumerate(skills_state):
                if s and is_terminal_state(s):
                    if self.intent_idxs[i] == j:
                        logger.debug("Intet {j} is terminated. Reset current intent from {j} to {self.default_intent}")
                        self.intent_idxs[i] = self.default_intent
            if (self.intent_idxs[i] == self.default_intent) or (self.intent_idxs[i] == self.intents.index('FAQ')):
                self.intent_idxs[i] = self.intents.index(intents[i])
            logger.debug(f"Intent index: {self.intent_idxs[i]}")
            result[i][self.intent_idxs[i]] = True
            for k in self.always_open:
                result[i][k] = True
        logger.info(f"Filter result: {result}")
        return result
