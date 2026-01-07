from ...domain.interfaces.istep_explainer import IStepExplainer
from ...domain.entities.step_result import StepResult
from ...domain.entities.transition import Transition


class StepExplainer(IStepExplainer):
    
    STATE_DESCRIPTIONS = {
        'q0': "Başlangıç durumu. Dış döngünün ilk adımını başlatır.",
        'q1': "İç döngünün ilk adımını başlatan durum.",
        'q2': "İlk 'B'yi '2'ye çevirerek sağa hareket eden durum.",
        'q3': "İç döngüde geriye dönüşü sağlayan durum.",
        'q4': (
            "İç döngünün sonraki adımlarını başlatan; "
            "iç döngü bitti ise dış döngünün geriye dönüşünü başlatan durum."
        ),
        'q5': (
            "Dış döngünün geriye dönüşünü sağlayan, "
            "bu arada 1'ler öbeğine eski görünümünü kazandıran durum."
        ),
        'q6': "Dış döngünün sonraki adımlarını başlatan durum.",
        'q7': (
            "Bitiş konfigürasyonunda, okuma kafasının "
            "2'ler öbeğinin başında olmasını sağlayan durumlar."
        ),
        'q8': (
            "Bitiş konfigürasyonunda, okuma kafasının "
            "2'ler öbeğinin başında olmasını sağlayan durumlar."
        ),
    }
    
    def explain_step(self, step_result: StepResult) -> str:
        if step_result.is_halted and not step_result.transition:
            return step_result.explanation or "Makine durdu."
        
        state_transition = (
            f"{step_result.previous_state.name} → {step_result.current_state.name}"
        )
        
        explanation_parts = [
            f"Adım {step_result.step_number}: Durum Geçişi",
            f"  Durum: {state_transition}",
            f"  Okunan Sembol: '{step_result.read_symbol}'",
            f"  Yazılan Sembol: '{step_result.write_symbol}'",
            f"  Hareket Yönü: {self._format_direction(step_result.direction)}",
            f"  Kafa Pozisyonu: {step_result.head_position}",
        ]
        
        current_state_desc = self.explain_state_purpose(
            step_result.current_state.name
        )
        explanation_parts.append(f"\n  Durum Açıklaması: {current_state_desc}")
        
        if step_result.transition:
            transition_desc = self.explain_transition(step_result.transition)
            explanation_parts.append(f"\n  Geçiş Açıklaması: {transition_desc}")
        
        tape_vis = self._format_tape_visualization(step_result)
        explanation_parts.append(f"\n  Şerit Durumu:\n{tape_vis}")
        
        algorithm_desc = self._explain_algorithm_step(step_result)
        if algorithm_desc:
            explanation_parts.append(f"\n  Algoritma Mantığı: {algorithm_desc}")
        
        return "\n".join(explanation_parts)
    
    def explain_transition(self, transition: Transition) -> str:
        direction_text = self._format_direction(transition.direction, with_article=True)
        
        return (
            f"{transition.from_state.name} durumunda '{transition.read_symbol}' "
            f"sembolü okundu, '{transition.write_symbol}' yazıldı, "
            f"{direction_text} hareket edildi ve {transition.to_state.name} "
            f"durumuna geçildi."
        )
    
    def explain_state_purpose(self, state_name: str) -> str:
        return self.STATE_DESCRIPTIONS.get(
            state_name, 
            "Durum açıklaması mevcut değil."
        )
    
    def _format_direction(self, direction: str, with_article: bool = False) -> str:
        if direction == 'L':
            return "sola" if with_article else "Sol"
        elif direction == 'R':
            return "sağa" if with_article else "Sağ"
        else:
            return "Yok"
    
    def _format_tape_visualization(self, step_result: StepResult) -> str:
        if not step_result.tape_snapshot:
            return "    (Boş şerit)"
        
        context = 7
        min_pos = min(step_result.tape_snapshot.keys())
        max_pos = max(step_result.tape_snapshot.keys())
        
        display_min = max(min_pos, step_result.head_position - context)
        display_max = min(max_pos, step_result.head_position + context)
        
        symbols = []
        positions = []
        for pos in range(display_min, display_max + 1):
            symbol = step_result.tape_snapshot.get(pos, 'B')
            display_symbol = symbol if symbol != 'B' else '□'
            symbols.append(display_symbol)
            positions.append(pos)
        
        tape_line = "    " + " ".join(f"{sym:^3}" for sym in symbols)
        pos_line = "    " + " ".join(f"{pos:^3}" for pos in positions)
        
        head_idx = step_result.head_position - display_min
        marker_line = "    " + "   " * head_idx + " ↑"
        
        return f"{tape_line}\n{pos_line}\n{marker_line}"
    
    def _explain_algorithm_step(self, step_result: StepResult) -> str:
        state = step_result.current_state.name
        read = step_result.read_symbol
        write = step_result.write_symbol
        prev_state = step_result.previous_state.name
        
        if prev_state == 'q0' and read == '0' and write == 'X':
            return (
                "İlk '0' sembolü 'X' ile işaretlendi. Bu, dış döngünün başlangıcını gösterir. "
                "Her '0' için, '1'ler öbeği kopyalanacak (m'yi n kez toplama işlemi)."
            )
        
        if state == 'q1' and read == '0' and write == '0':
            return "Dış döngüde: '0' sembollerini geçiyoruz. İlk '1'e ulaşmayı bekliyoruz."
        
        if prev_state == 'q1' and read == '1' and write == 'Y':
            return (
                "İlk '1' sembolüne ulaşıldı ve 'Y' ile işaretlendi. "
                "Bu, iç döngünün başlangıcını gösterir. "
                "Şimdi bu '1' öbeğini kopyalayacağız."
            )
        
        if state == 'q2' and read in ['1', '2'] and write == read:
            return (
                "İç döngüde: Mevcut '1'leri ve oluşturulmuş '2'leri geçiyoruz. "
                "İlk boş hücreyi (B) arıyoruz."
            )
        
        if prev_state == 'q2' and read == 'B' and write == '2':
            return (
                "İlk boş hücreye (B) ulaşıldı ve '2' yazıldı. "
                "Bu, çarpma sonucunun bir parçasıdır. "
                "Şimdi geriye dönüp bir sonraki '1'i işleyeceğiz."
            )
        
        if state == 'q3' and read in ['1', '2'] and write == read:
            return (
                "İç döngüde geriye dönüş: '1'leri ve '2'leri geçerek "
                "işaretlenmiş 'Y' sembolüne geri dönüyoruz."
            )
        
        if prev_state == 'q3' and read == 'Y' and write == 'Y':
            return (
                "İşaretlenmiş 'Y' sembolüne geri dönüldü. "
                "Eğer daha fazla '1' varsa, iç döngü devam edecek. "
                "Yoksa dış döngünün geriye dönüşüne geçilecek."
            )
        
        if prev_state == 'q4' and read == '1' and write == 'Y':
            return (
                "İç döngü devam ediyor: Bir sonraki '1' 'Y' ile işaretleniyor. "
                "Bu '1' için de '2' yazılacak."
            )
        
        if prev_state == 'q4' and read == '2' and write == '2':
            return (
                "İç döngü tamamlandı. Tüm '1'ler işlendi. "
                "Şimdi dış döngünün geriye dönüşüne geçiliyor."
            )
        
        if state == 'q5' and read == '0' and write == '0':
            return (
                "Dış döngüde geriye dönüş: '0' sembollerini geçerek "
                "işaretlenmiş 'X' sembolüne geri dönüyoruz."
            )
        
        if prev_state == 'q5' and read == 'Y' and write == '1':
            return (
                "İşaretlenmiş 'Y' sembolleri tekrar '1'e çevriliyor. "
                "Bu, 1'ler öbeğinin orijinal görünümünü geri kazandırır."
            )
        
        if prev_state == 'q5' and read == 'X' and write == 'X':
            return (
                "İşaretlenmiş 'X' sembolüne geri dönüldü. "
                "Eğer daha fazla '0' varsa, dış döngü devam edecek. "
                "Yoksa bitiş konfigürasyonuna geçilecek."
            )
        
        if prev_state == 'q6' and read == '0' and write == 'X':
            return (
                "Dış döngü devam ediyor: Bir sonraki '0' 'X' ile işaretleniyor. "
                "Bu '0' için de '1'ler öbeği kopyalanacak."
            )
        
        if prev_state == 'q6' and read == '1' and write == '1':
            return (
                "Tüm '0'ler işlendi. Dış döngü tamamlandı. "
                "Şimdi bitiş konfigürasyonuna geçiliyor: "
                "kafa 2'ler öbeğinin başına konumlandırılacak."
            )
        
        if state == 'q7' and read == '1' and write == '1':
            return (
                "Bitiş konfigürasyonu: '1'ler öbeğini geçerek "
                "2'ler öbeğinin başına ulaşıyoruz."
            )
        
        if prev_state == 'q7' and read == '2' and write == '2':
            return (
                "2'ler öbeğinin başına ulaşıldı. "
                "Makine son konfigürasyonuna geçiyor."
            )
        
        if state == 'q8' and read == '1' and write == '1':
            return (
                "Son konfigürasyon: Kafa 2'ler öbeğinin başında. "
                "Hesaplama tamamlandı. Sonuç: n×m adet '2'."
            )
        
        return ""

