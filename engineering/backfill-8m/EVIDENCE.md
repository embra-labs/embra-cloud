# Số liệu và phương pháp đối chiếu

Tài liệu đi kèm [Backfill 8 triệu dòng: dữ liệu đúng, nhưng latency không đạt](article.md), xuất bản ngày 08/10/2026.

## Những gì được công bố

- [CSV latency](data/latency.csv): số mẫu, p99, baseline, loại metric và quy tắc chọn cửa sổ cho từng lượt.
- [Kết quả kiểm toàn vẹn và nguồn đầu vào](data/evidence.json): aggregate được chọn, checkpoint và SHA-256 của tệp nguồn.
- [Script tạo hình](build.py) và [phiên bản thư viện](requirements.txt): dựng lại hình từ aggregate.
- [Bài viết dạng Markdown](article.md).

Raw request log và các báo cáo vận hành gốc chưa được công bố. Gói này cho phép kiểm các con số được trình bày và dựng lại hình; chưa đủ để tự tái chạy workload hoặc kiểm độc lập toàn bộ phép đo từ request thô. Hash nhận diện tệp đầu vào nội bộ, không tự chứng minh phép đo chính xác.

## Nguồn của các kết luận

| Nội dung | Nguồn dùng khi biên tập | Mức kiểm chứng |
| :--- | :--- | :--- |
| Cấu hình và sự cố runner 28/9 | Báo cáo lab 28/9 | Đối chiếu với summary và nhật ký executor |
| Latency 28/9 | Summary của ba lượt `20260928T044810Z`, `20260928T051000Z`, `20260928T072200Z` | Trích nguyên số liệu; không tính lại request log ngày này |
| Toàn vẹn và checkpoint 28/9 | Final verifier, audit, M4 executor log của lượt cuối ngày | Kiểm tổng request/ACK, số dòng, hai checkpoint; xuất trường chọn lọc |
| Latency hai lượt sau | Events và request log của `20260929T075832Z`, `20260929T155607Z` | Tính lại p99 theo công thức bên dưới |
| Toàn vẹn lượt cuối | Verifier của `20260929T155607Z` | Trích số liệu; không chạy lại workload |
| I/O, sampler TXG và sự cố archive trước vòng cuối | Báo cáo thử nghiệm và ghi chép vận hành 29–30/9 | Tóm tắt quan sát; chưa tái phân tích tương quan hay xác lập nhân quả |

Phân loại I/O cao trong báo cáo gốc dùng mẫu cùng giây có `io_ms > 700` hoặc `write_ms > 500`; request chậm là trên 200 ms. Đây là ngưỡng của phân tích đó, không phải ngưỡng sức khỏe chung cho mọi thiết bị. Chưa có snapshot mã thực thi đầy đủ của từng lượt trong gói công khai.

## Cách chọn request và tính percentile

Ngày 28/9 giữ nguyên số liệu do `summarize.py` tạo: request giao với cửa sổ apply (`overlap_apply_window`). Tổng 1.269.965 request là tổng toàn bộ ba lượt, không phải tổng ba hàng trong biểu đồ. Ba hàng biểu đồ chỉ gồm request trong pha backfill tương ứng.

Hai lượt sau được tính lại theo cùng quy tắc rõ ràng: `apply_start <= request.start < apply_end`. Với mỗi mẫu:

```text
start_to_end_ms = request.ms
scheduled_to_end_ms = (request.end - request.scheduled) * 1000
p99 = sorted(samples)[ceil(len(samples) * 0.99) - 1]
```

Không lấy hiệu hai percentile để suy ra percentile thời gian chờ. Không trộn metric SQL với HTTP. CSV lưu millisecond, dùng dấu chấm thập phân. Bảng bài viết dùng quy ước Việt Nam; nhãn số trong biểu đồ dùng dấu chấm thập phân và dấu phẩy phân nhóm hàng nghìn.

| Lượt | Pha | n theo quy tắc bắt đầu trong cửa sổ | p99 từ lịch phát (ms) |
| :--- | :--- | ---: | ---: |
| 29/9, lượt 4 | M3 | 457.437 | 1.361,706 |
| 29/9, lượt 4 | M4 | 835.749 | 1.651,383 |
| Đêm 29–30/9, lượt 7 | M3 | 434.468 | 1.848,479 |
| Đêm 29–30/9, lượt 7 | M4 | 128.260 | 2.485,287 |

Báo cáo lượt 7 ghi n là 434.470 và 128.254, hơi khác phép trích hiện tại. Chưa xác minh đầy đủ quy tắc lọc của bộ phân tích cũ; bài dùng định nghĩa và số n từ script đính kèm. p99 làm tròn tới một chữ số thập phân khớp báo cáo. Không coi đây là hai phép trích giống hệt nhau.

Baseline scheduled-to-end p99 của lượt 4 là 815,892 ms; lượt 7 là 1.601,807 ms. Baseline lượt cuối đã vượt mục tiêu một giây trước apply. Vì vậy không thể quy toàn bộ p99 khi apply cho migration. Các lượt còn khác topology và tải; biểu đồ không chứng minh tác dụng nhân quả của throttle.

## Hai vấn đề khác nhau với metric lịch phát

Hai lượt đầu 28/9 có lỗi căn chỉnh mốc đồng hồ: không sử dụng scheduled-to-end của chúng. Lượt cuối 28/9 đã sửa mốc và báo `schedule_metrics_valid=true`.

Summary lượt 4 ngày 29/9 báo `schedule_metrics_valid=false` do thiếu bản `traffic-config.json` từ máy tạo tải riêng, theo báo cáo lượt 4. Đây không phải cùng lỗi đồng hồ ngày 28/9. Bài sử dụng phép tính lại trên request log, có giá trị làm tròn khớp báo cáo; điều này không thay thế việc lưu đủ cấu hình generator cho một benchmark tái lập độc lập.

## Giới hạn kết luận

- Verifier kiểm các invariant cụ thể của fixture, không chứng minh mọi migration, crash phần cứng hoặc failover đều an toàn.
- Dữ liệu kiểm cuối vòng 7 đã được seed lại sau sự cố trước đó. Không dùng kết quả này để khẳng định đã khôi phục nguyên vẹn dataset trước sự cố.
- Quan sát I/O cùng giây với request chậm là tương quan theo ngưỡng phân loại của báo cáo. Không diễn giải thành phần trăm latency do đĩa gây ra.
- Topology và commit/resume là sơ đồ giải thích. Hai biểu đồ latency dùng số liệu thật; cover là hình chữ biên tập.
- Gói này chỉ xuất scalar và aggregate được chọn. Không sao chép request thô, địa chỉ máy, payload hoặc credential vào bài.

## Dựng lại hình từ số liệu công bố

Tải `build.py`, `requirements.txt`, `article.md`, tài liệu này dưới tên `EVIDENCE.md` và hai tệp trong thư mục `data/`. Giữ nguyên cấu trúc thư mục rồi chạy:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
```

Script tạo thư mục `assets/`, các biểu đồ, cover và bản preview HTML local. Chế độ `--source-root` chỉ dùng được khi có checkout dữ liệu lab gốc; dữ liệu đó không nằm trong gói công khai. Các lượt thử không được chạy lại khi biên tập bài.

Có câu hỏi về phương pháp hoặc phát hiện sai số? [Mở issue trên repository website](https://github.com/embra-labs/embra-cloud/issues) hoặc liên hệ [hello@embra.cloud](mailto:hello@embra.cloud). Không đưa dữ liệu ứng dụng hoặc thông tin truy cập vào issue công khai.
