import com.gaotu.renewal.*;
import com.gaotu.domain.teacher.TeacherFacade;
import com.gaotu.feignclient.order.OrderInfoAdapterFeignService;
import com.gaotu.feignclient.order.dto.OrderInfoDTO;
import com.gaotu.feignclient.coursecenter.dto.*;
import com.gaotu.request.*;
import com.gaotu.vo.renewal.ClazzDetailDTO;
import org.springframework.test.util.ReflectionTestUtils;
import java.util.*;
import java.util.stream.Collectors;
import static org.mockito.Mockito.*;
import static org.mockito.Matchers.*;
public class DisplayProbe {
 public static void main(String[] args) {
  RenewalService svc=new RenewalService();
  RenewalDataService data=mock(RenewalDataService.class);
  OrderInfoAdapterFeignService orders=mock(OrderInfoAdapterFeignService.class);
  TeacherFacade teachers=mock(TeacherFacade.class);
  ReflectionTestUtils.setField(svc,"renewalDataService",data);
  ReflectionTestUtils.setField(svc,"orderInfoAdapterFeignService",orders);
  ReflectionTestUtils.setField(svc,"teacherFacade",teachers);
  ReflectionTestUtils.setField(svc,"teacherSize",5);
  List<ClazzDTO> classes=new ArrayList<>(); List<ProductCatDTO> cats=new ArrayList<>();
  for(long id:Arrays.asList(101L,102L,103L,104L)) {
   ClazzDTO c=new ClazzDTO();c.setNumber(id);c.setCourseNumber(1L);c.setProductType(2);c.setTeacherNumbers(Collections.emptyList());classes.add(c);
   ProductCatDTO cat=new ProductCatDTO();cat.setProductSkuNumber(id);cat.setProductType(2);cats.add(cat);
  }
  CourseDTO course=new CourseDTO();course.setNumber(1L);course.setSubjects(Collections.emptyList());
  when(data.getClazzByClazzNumbersWithCache(anyList())).thenReturn(classes);
  when(data.getCourseByNumbersWithCache(anyList())).thenReturn(Collections.singletonList(course));
  when(data.getCourseCenterDictionarySubjectCache()).thenReturn(Collections.emptyList());
  when(teachers.mapTeacherByNumbers(anyList())).thenReturn(Collections.emptyMap());
  ProductListRequest req=new ProductListRequest();req.setProductNumberList(cats);
  for(boolean mixed:Arrays.asList(false,true)) {
   List<OrderInfoDTO> paid=new ArrayList<>();
   if(mixed)for(long id:Arrays.asList(101L,103L)){OrderInfoDTO o=new OrderInfoDTO();o.setClazzNumber(id);o.setOrderStatus(2);paid.add(o);}
   when(orders.ListByClazzNumbersAndUserIds(anyList(),anyLong())).thenReturn(paid);
   List<ClazzDetailDTO> result=svc.productList(req,1L);
   System.out.println("PROBE productList mixed="+mixed+" ids="+result.stream().map(ClazzDetailDTO::getProductSkuNumber).collect(Collectors.toList()));
  }
  List<ClazzDetailDTO> display=new ArrayList<>();
  for(int[] spec:new int[][]{{1,1,1,1},{2,0,0,3},{3,0,1,2},{4,0,1,1},{5,0,1,1},{6,0,0,1}}){
   ClazzDetailDTO d=new ClazzDetailDTO();d.setProductSkuNumber((long)spec[0]);d.setSignUp(spec[1]);d.setForceBuy(spec[2]==1);d.setRecommendType(spec[3]);display.add(d);
  }
  ReflectionTestUtils.invokeMethod(svc,"sortClazzDetailDTOsForDisplay",display);
  System.out.println("PROBE display priority="+display.stream().map(ClazzDetailDTO::getProductSkuNumber).collect(Collectors.toList()));
 }
}
