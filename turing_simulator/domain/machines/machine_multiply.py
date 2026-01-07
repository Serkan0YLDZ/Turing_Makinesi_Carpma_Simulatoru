from typing import Dict, Tuple
from ..entities.state import State
from ..entities.transition import Transition
from ..entities.turing_machine import TuringMachine


def create_multiply_machine() -> TuringMachine:
    q0 = State(
        name="q0",
        is_initial=True,
        description="Başlangıç durumu. Dış döngünün ilk adımını başlatır."
    )
    q1 = State(
        name="q1",
        description="İç döngünün ilk adımını başlatan durum."
    )
    q2 = State(
        name="q2",
        description="İlk 'B'yi '2'ye çevirerek sağa hareket eden durum."
    )
    q3 = State(
        name="q3",
        description="İç döngüde geriye dönüşü sağlayan durum."
    )
    q4 = State(
        name="q4",
        description=(
            "İç döngünün sonraki adımlarını başlatan; "
            "iç döngü bitti ise dış döngünün geriye dönüşünü başlatan durum."
        )
    )
    q5 = State(
        name="q5",
        description=(
            "Dış döngünün geriye dönüşünü sağlayan, "
            "bu arada 1'ler öbeğine eski görünümünü kazandıran durum."
        )
    )
    q6 = State(
        name="q6",
        description="Dış döngünün sonraki adımlarını başlatan durum."
    )
    q7 = State(
        name="q7",
        description=(
            "Bitiş konfigürasyonunda, okuma kafasının "
            "2'ler öbeğinin başında olmasını sağlayan durumlar."
        )
    )
    q8 = State(
        name="q8",
        description=(
            "Bitiş konfigürasyonunda, okuma kafasının "
            "2'ler öbeğinin başında olmasını sağlayan durumlar."
        )
    )
    
    states = [q0, q1, q2, q3, q4, q5, q6, q7, q8]
    
    transitions: Dict[Tuple[State, str], Transition] = {
        (q0, '0'): Transition(q0, q1, '0', 'X', 'R'),
        (q1, '0'): Transition(q1, q1, '0', '0', 'R'),
        (q1, '1'): Transition(q1, q2, '1', 'Y', 'R'),
        (q2, '1'): Transition(q2, q2, '1', '1', 'R'),
        (q2, '2'): Transition(q2, q2, '2', '2', 'R'),
        (q2, 'B'): Transition(q2, q3, 'B', '2', 'L'),
        (q3, '1'): Transition(q3, q3, '1', '1', 'L'),
        (q3, '2'): Transition(q3, q3, '2', '2', 'L'),
        (q3, 'Y'): Transition(q3, q4, 'Y', 'Y', 'R'),
        (q4, '1'): Transition(q4, q2, '1', 'Y', 'R'),
        (q4, '2'): Transition(q4, q5, '2', '2', 'L'),
        (q5, '0'): Transition(q5, q5, '0', '0', 'L'),
        (q5, 'X'): Transition(q5, q6, 'X', 'X', 'R'),
        (q5, 'Y'): Transition(q5, q5, 'Y', '1', 'L'),
        (q6, '0'): Transition(q6, q1, '0', 'X', 'R'),
        (q6, '1'): Transition(q6, q7, '1', '1', 'R'),
        (q7, '1'): Transition(q7, q7, '1', '1', 'R'),
        (q7, '2'): Transition(q7, q8, '2', '2', 'L'),
        (q8, '1'): Transition(q8, q8, '1', '1', 'R'),
    }
    
    machine = TuringMachine(
        states=states,
        initial_state=q0,
        transitions=transitions,
        blank_symbol='B',
        final_states=[]
    )
    
    return machine

