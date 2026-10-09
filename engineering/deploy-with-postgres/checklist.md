# Checklist deploy app có Postgres

Mẫu để điền khi diễn tập, không phải kết quả kiểm thử của Embra.
Hướng dẫn: https://embra.cloud/engineering/deploy-with-postgres/

- Ngày / người thực hiện:
- Môi trường test / cấu hình (không ghi secret):
- Phiên bản app trước / sau:
- Phiên bản schema trước / sau:
- Mã đơn thử / dữ liệu cần đối chiếu:
- Mức lỗi và latency trước thử:
- Ngưỡng dừng / thời gian quan sát:
- Người quyết định dừng / nơi lưu phương án xử lý sự cố:
- Mốc backup / nơi restore cách ly:
- Phiên bản có thể rollback với schema sau migration:

| Phép kiểm | Bằng chứng cần lưu | Kết quả của bạn |
| :--- | :--- | :--- |
| Thay container | Đơn thử vẫn có đúng trạng thái/tổng tiền; checksum ảnh khớp nếu có | Chưa chạy |
| Cấu hình môi trường | App trỏ đúng DB/storage thử; không lộ credential | Chưa chạy |
| Phiên bản chưa sẵn sàng | Request không được chuyển sang bản chưa qua readiness | Chưa chạy |
| Quay lại code cũ | Bản cũ chạy được với schema hiện tại trong phạm vi đã thử | Chưa chạy |
| Restore backup | App đọc được đơn thử từ DB phục hồi riêng; file tham chiếu tồn tại nếu có | Chưa chạy |
| Mốc và thời gian phục hồi | Ghi mốc dữ liệu, thời gian thực hiện và phần dữ liệu không được khôi phục | Chưa chạy |

## Quyết định

- Kết quả: Chưa chạy / Đạt trong phạm vi đã thử / Chưa đạt
- Sai lệch và bằng chứng:
- Trạng thái code khi dừng:
- Trạng thái database khi dừng:
- Dữ liệu không có trong bản restore:
- Việc phải làm trước lần deploy tiếp theo:

Không điền token, mật khẩu hoặc dữ liệu khách hàng vào bản ghi này.
