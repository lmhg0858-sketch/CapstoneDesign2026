package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.AnalysisResult;
import org.springframework.stereotype.Component;

@Component
public class HyperlipidemiaComparator implements DiseaseComparator {
    @Override public String getDiseaseName() { return "고지혈증"; }

    @Override
    public AnalysisResult evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        AnalysisResult res = new AnalysisResult(getDiseaseName());
        boolean isM = "MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender());
        
        int cholS = (n.getCholesterol() >= 120) ? 0 : (n.getCholesterol() >= 60 ? 50 : 100);
        int fatS = (n.getFat() >= (isM ? 50 : 40)) ? 0 : (n.getFat() >= (isM ? 25 : 20) ? 50 : 100);
        int sodS = (n.getSodium() >= 1200) ? 0 : (n.getSodium() >= 600 ? 50 : 100);

        res.addNutrient("콜레스테롤", cholS);
        res.addNutrient("지방", fatS);
        res.addNutrient("나트륨", sodS);
        res.calculateFinal(cholS * 0.6 + fatS * 0.3 + sodS * 0.1);
        return res;
    }
}