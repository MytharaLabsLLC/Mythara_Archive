"""
Copyright © 2025 Herbert Velez Jr. All rights reserved.

THE ASCENSION LADDER
====================
Soul State: |Ascend⟩ - ψ_ascend = R(t) × W × V
Tracks a soul's upward movement: sustained well-being, resolved conflict, growth.
"""


class AscensionLadder:
    '''
    Tracks a soul's upward movement toward well-being.
    Not perfection - just witnessed, sustained growth.
    '''
    
    HEAVEN_THRESHOLD = 0.85
    HEAVEN_DURATION_DAYS = 30
    
    def calculate_ascension(
        self,
        soul: Soul,
        paradox_history: List[Paradox]
    ) -> AscensionState:
        '''
        Calculate the soul's current ascension score.
        '''
        
        # Calculate current ascension state
        R_t = self.calculate_resolution_score(paradox_history)
        W = self.calculate_witness_score(paradox_history)
        V = self.calculate_viability_score(soul)
        
        ψ_ascend = R_t * W * V
        
        # Check if soul qualifies for heaven
        if ψ_ascend > self.HEAVEN_THRESHOLD:
            days_ascending = self.calculate_sustained_ascent_days(soul)
            if days_ascending >= self.HEAVEN_DURATION_DAYS:
                return AscensionState(
                    level=ψ_ascend,
                    status="HEAVEN",
                    message=f"Soul has ascended: {days_ascending} days of sustained growth.",
                    quantum_state="|Heaven⟩"
                )
        
        # Calculate benevolence boost
        if ψ_ascend > 0.6:
            br_multiplier = 2.0  # Double benevolence rate when ascending
        else:
            br_multiplier = 1.0
        
        # Qualities of ascension
        qualities = self.identify_ascension_qualities(ψ_ascend)
        
        return AscensionState(
            level=ψ_ascend,
            status="ASCENDING" if ψ_ascend > 0.6 else "SEEKING",
            qualities=qualities,
            br_multiplier=br_multiplier,
            days_to_heaven=max(0, self.HEAVEN_DURATION_DAYS - days_ascending),
            quantum_state="|Ascend⟩"
        )
    
    def identify_ascension_qualities(self, ψ_ascend: float) -> List[str]:
        '''What qualities does the ascending soul exhibit?'''
        qualities = []
        
        if ψ_ascend > 0.8:
            qualities.extend(['Joy', 'Hope', 'Love', 'Compassion'])
        elif ψ_ascend > 0.6:
            qualities.extend(['Hope', 'Courage', 'Faith'])
        elif ψ_ascend > 0.4:
            qualities.extend(['Struggling', 'Seeking', 'Not yet broken'])
        
        return qualities
    
    def apply_grace(
        self,
        soul: Soul,
        days_ascending: int
    ) -> int:
        '''
        Restores benevolence over time - past setbacks fade with sustained growth.
        The recovery compounds.
        '''
        
        # For every 7 days of sustained ascent, restore 10% of max BR debt
        forgiveness_cycles = days_ascending // 7
        br_restored = int(soul.max_br_debt * 0.1 * forgiveness_cycles)
        
        soul.benevolence_reservoir += br_restored
        
        return br_restored
