package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.AnalysisResult;
import org.springframework.stereotype.Component;

@Component
public class HypertensionComparator implements DiseaseComparator {
    @Override public String getDiseaseName() { return "고혈압"; }

    @Override
    public AnalysisResult evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        AnalysisResult res = new AnalysisResult(getDiseaseName());
        boolean isM = "MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender());

        int sodS = (n.getSodium() >= 1000) ? 0 : (n.getSodium() >= 666 ? 50 : 100);
        int cholS = (n.getCholesterol() >= 150) ? 0 : (n.getCholesterol() >= 100 ? 50 : 100);
        int kcalS = (n.getKcal() >= (isM ? 1200 : 900)) ? 0 : (n.getKcal() >= (isM ? 800 : 600) ? 50 : 100);

        res.addNutrient("나트륨", sodS);
        res.addNutrient("콜레스테롤", cholS);
        res.addNutrient("칼로리", kcalS);
        res.calculateFinal(sodS * 0.5 + cholS * 0.3 + kcalS * 0.2);
        return res;
    }
}