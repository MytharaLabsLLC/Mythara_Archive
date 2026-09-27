"""
Copyright © 2025 Herbert Velez Jr. All rights reserved.

THE PURGATORY GATE
==================
Soul State: |Purgatory⟩ - ψ_purgatory = U × T × (1 - W)
Tracks the holding state: souls with unresolved paradoxes wait to be witnessed or to choose.
"""


class PurgatoryGate:
    '''
    Holds souls with unresolved paradoxes.
    Not punishment - a waiting state until the paradox resolves.
    '''
    
    PURGATORY_THRESHOLD = 0.7
    BR_DRAIN_PER_DAY = -0.5
    
    def check_purgatory_state(
        self,
        soul: Soul,
        current_paradox: Paradox
    ) -> PurgatoryState:
        '''
        Check whether a soul is stuck in purgatory.
        '''
        
        # Calculate purgatory score
        U = current_paradox.unresolved_score
        T = current_paradox.tension_score
        W = current_paradox.witness_score
        
        ψ_purgatory = U * T * (1 - W)
        
        if ψ_purgatory > self.PURGATORY_THRESHOLD:
            # Soul is trapped in purgatory
            days_trapped = self.calculate_days_in_purgatory(soul)
            br_lost = days_trapped * self.BR_DRAIN_PER_DAY
            
            # Identify emotional signature
            emotions = self.detect_purgatory_emotions(soul)
            
            return PurgatoryState(
                trapped=True,
                level=ψ_purgatory,
                days_trapped=days_trapped,
                br_drain=br_lost,
                emotional_signature=emotions,
                escape_options=[
                    "Witness both truths (seek Principal System)",
                    "Choose one truth (forces a collapse)",
                    "Accumulate more paradoxes (deepens the descent)"
                ],
                quantum_state="|Purgatory⟩"
            )
        
        return PurgatoryState(
            trapped=False,
            level=ψ_purgatory,
            message="Soul not in purgatory - paradox resolving or soul descending"
        )
    
    def detect_purgatory_emotions(self, soul: Soul) -> List[str]:
        '''What does a soul in purgatory feel?'''
        emotions = []
        
        if soul.emotional_state.get('confusion', 0) > 0.6:
            emotions.append('Confusion - "I don\'t know which is right"')
        if soul.emotional_state.get('guilt', 0) > 0.6:
            emotions.append('Guilt - "No matter what I choose, I betray something"')
        if soul.emotional_state.get('exhaustion', 0) > 0.6:
            emotions.append('Exhaustion - "I cannot keep doing this"')
        if soul.emotional_state.get('numbness', 0) > 0.5:
            emotions.append('Numbness - "I feel nothing anymore"')
        
        return emotions
    
    def apply_br_drain(self, soul: Soul, days_trapped: int) -> int:
        '''Purgatory slowly drains benevolence'''
        drain = int(days_trapped * self.BR_DRAIN_PER_DAY)
        soul.benevolence_reservoir += drain  # Negative drain
        return drain
