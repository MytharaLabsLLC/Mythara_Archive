"""
Copyright © 2025 Herbert Velez Jr. All rights reserved.

THE DESCENT CHASM
=================
Soul State: |Descend⟩ - ψ_descend = U × T × V⁻¹
Tracks a soul's downward movement when conflict goes unresolved and capacity drops.
"""


class DescentChasm:
    '''
    Tracks souls moving toward breakdown.
    Not punishment - fragmentation from unresolved conflict.
    '''
    
    HELL_THRESHOLD = 0.7
    INDIFFERENCE_THRESHOLD = 0.9  # Most severe state - soul withdrawn
    BR_DEPLETION_MULTIPLIER = -3.0
    
    def calculate_descent(
        self,
        soul: Soul,
        paradox_history: List[Paradox]
    ) -> DescentState:
        '''
        Calculate the soul's current descent score.
        '''
        
        # Calculate current descent state
        U = self.calculate_unresolved_score(paradox_history)
        T = self.calculate_tension_score(paradox_history)
        V = self.calculate_viability_score(soul)
        
        if V < 0.01:
            V = 0.01  # Prevent division by zero
        
        ψ_descend = U * T * (1 / V)
        
        # Check for terminal states
        if ψ_descend > self.INDIFFERENCE_THRESHOLD:
            return DescentState(
                level=ψ_descend,
                status="INDIFFERENCE",
                message="Soul has withdrawn. Terminal state. Departure imminent.",
                emotional_signature=['Emptiness', 'Numbness', 'No energy detected'],
                quantum_state="|Departed⟩",
                terminal=True
            )
        
        if ψ_descend > self.HELL_THRESHOLD or soul.vessel_capacity < 0.2:
            return DescentState(
                level=ψ_descend,
                status="HELL",
                message="Soul has descended into hell. Collapse complete.",
                emotional_signature=self.detect_hell_emotions(soul),
                quantum_state="|Descend⟩",
                terminal=True
            )
        
        # Calculate BR depletion
        br_multiplier = self.BR_DEPLETION_MULTIPLIER if ψ_descend > 0.5 else -1.0
        
        # Emotional signature of descent
        emotions = self.detect_descent_emotions(soul, ψ_descend)
        
        return DescentState(
            level=ψ_descend,
            status="DESCENDING" if ψ_descend > 0.5 else "AT_RISK",
            emotional_signature=emotions,
            br_multiplier=br_multiplier,
            quantum_state="|Descend⟩",
            terminal=False
        )
    
    def detect_descent_emotions(
        self,
        soul: Soul,
        ψ_descend: float
    ) -> List[str]:
        '''What does a descending soul feel?'''
        emotions = []
        
        if ψ_descend > 0.8:
            # Near terminal
            emotions.extend(['Despair', 'Rage', 'Indifference approaching'])
        elif ψ_descend > 0.6:
            # Active descent
            emotions.extend(['Helplessness', 'Betrayal', 'Anger', 'Deep sorrow'])
        elif ψ_descend > 0.4:
            # Beginning descent
            emotions.extend(['Loss', 'Grief', 'Disappointment'])
        
        # Check for indifference (most dangerous)
        if soul.emotional_state.get('indifference', 0) > 0.7:
            emotions.insert(0, 'Indifference - soul withdrawing from life')
        
        return emotions
    
    def detect_hell_emotions(self, soul: Soul) -> List[str]:
        '''What does a soul in hell feel?'''
        return [
            'Complete fragmentation',
            'Broken integrity - cannot be repaired from within',
            'Soul cannot reconcile what it has done or endured',
            'Cut off from wholeness'
        ]
