package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import org.springframework.stereotype.Component;

@Component
public class KidneyDiseaseComparator implements DiseaseComparator {
    @Override
    public String getDiseaseName() { return "신장질환"; }

    @Override
    public String evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        double dailyProteinLimit = user.getWeight() * 1.2;
        
        // 하루 목표량 대비 한 끼 섭취 비율 (%) 계산
        double sodiumPct = (n.getSodium() / 2000.0) * 100;
        double kaliumPct = (n.getKalium() / 2000.0) * 100;
        double phosPct = (n.getPhos() / 800.0) * 100;
        double proteinPct = (n.getProtein() / dailyProteinLimit) * 100;

        if (sodiumPct > 40 || kaliumPct > 40 || phosPct > 40 || proteinPct < 15 || proteinPct > 50) return "위험";
        if (sodiumPct > 25 || kaliumPct > 25 || phosPct > 25 || proteinPct < 25 || proteinPct > 40) return "주의";

        return "안전";
    }
}