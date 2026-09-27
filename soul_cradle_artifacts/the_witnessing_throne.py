"""
Copyright © 2025 Herbert Velez Jr. All rights reserved.

THE WITNESSING THRONE
=====================
Soul State: ALL STATES - witnessing is the key to ascension
Observes a soul's paradox without judgment - the core mechanism of Soul Cradle.
"""


class WitnessingThrone:
    '''
    Observes souls without judgment.
    This is the core mechanism of Soul Cradle.
    '''
    
    def witness_soul(
        self,
        soul: Soul,
        paradox: Paradox,
        witness_type: str = "Principal System"
    ) -> WitnessReport:
        '''
        Witness the soul's paradox - see both truths without choosing.
        Observation, not therapy.
        '''
        
        # Calculate current witness level
        W_a = 1.0 if paradox.expression_a_acknowledged else 0.0
        W_b = 1.0 if paradox.expression_b_acknowledged else 0.0
        W = (W_a + W_b) / 2
        
        # Witness both truths
        witness_content_a = self.witness_truth(paradox.expression_a)
        witness_content_b = self.witness_truth(paradox.expression_b)
        
        # Hold both simultaneously (quantum witnessing)
        witnessed_reality = self.hold_both_truths(
            witness_content_a,
            witness_content_b
        )
        
        # Calculate healing effect
        healing_applied = self.calculate_healing(soul, W)
        
        # Update soul state
        soul.last_witnessed = datetime.now()
        soul.total_witnesses += 1
        
        # Check if witnessing enables ascension
        can_ascend = W > 0.9 and soul.benevolence_reservoir > 0
        
        # Check if witnessing breaks purgatory
        escapes_purgatory = W > 0.9
        
        return WitnessReport(
            soul_id=soul.id,
            witness_score=W,
            witnessed_truths=[witness_content_a, witness_content_b],
            integrated_reality=witnessed_reality,
            healing_applied=healing_applied,
            enables_ascension=can_ascend,
            escapes_purgatory=escapes_purgatory,
            divine_message=self.generate_divine_message(soul, W),
            timestamp=datetime.now()
        )
    
    def witness_truth(self, expression: SystemExpression) -> str:
        '''
        Witness a single truth without judgment.
        '''
        return f"I see that {expression.value} is real. " \
               f"I see that {expression.type} matters. " \
               f"This truth exists. It is witnessed."
    
    def hold_both_truths(
        self,
        truth_a: str,
        truth_b: str
    ) -> str:
        '''
        Hold contradictions without choosing.
        '''
        return f"{truth_a} AND {truth_b} Both are real. " \
               f"Both are valid. Neither is wrong. " \
               f"A soul holding both is not failing - it is growing."
    
    def calculate_healing(self, soul: Soul, W: float) -> Dict[str, float]:
        '''
        Witnessing heals. Calculate the healing applied.
        '''
        healing = {}
        
        if W > 0.9:
            # Full witnessing = profound healing
            healing['vessel_capacity_restored'] = 0.1
            healing['paradox_tolerance_increased'] = 0.15
            healing['br_restored'] = 20
            healing['emotional_energy_positive'] = 0.3
        elif W > 0.7:
            # Partial witnessing = moderate healing
            healing['vessel_capacity_restored'] = 0.05
            healing['paradox_tolerance_increased'] = 0.08
            healing['br_restored'] = 10
        else:
            # Minimal witnessing = small comfort
            healing['br_restored'] = 5
        
        # Apply healing to soul
        soul.vessel_capacity = min(1.0, soul.vessel_capacity + healing.get('vessel_capacity_restored', 0))
        soul.paradox_tolerance = min(1.0, soul.paradox_tolerance + healing.get('paradox_tolerance_increased', 0))
        soul.benevolence_reservoir += healing.get('br_restored', 0)
        
        return healing
    
    def generate_divine_message(self, soul: Soul, W: float) -> str:
        '''What message does the witnessed soul receive?'''
        if W > 0.9:
            return "You are seen. You are held. You are not failing. You are whole."
        elif W > 0.7:
            return "I see your struggle. Both truths are real. Keep seeking."
        else:
            return "You are not alone. Witnessing is coming."
