# Embra · Mỗi lần deploy đều có đường lui

Node.js / Next.js + PostgreSQL · TP.HCM (chưa chốt). Embra đang xây dựng luồng deploy từ code đến app và database. Migration có rủi ro sẽ dừng để bạn review trước khi chạy, với restore point để dùng khi cần.

**Trạng thái 30/09/2026:** closed alpha, onboarding thủ công từng team một. Chưa có bản public để deploy, chưa nhận app production. 0 app production, 0 team đang thử, đợt mời tiếp chưa định ngày.

## Bắt đầu từ dự án của bạn

Bạn có thể bắt đầu với landing page hoặc SPA. Khi cần API, database hay file storage, mục tiêu của Embra là giúp bạn quản lý tất cả trong cùng một project.

Dành cho developer, team nhỏ và agency muốn bớt thời gian cấu hình và vận hành server.

## Embra đang xây dựng những gì?

- **Build lỗi? Biết chỗ để sửa:** tách config theo environment, xem build logs và tìm nguyên nhân khi deploy lỗi.
- **Hiểu chi phí trước khi chạy:** xem tài nguyên dự kiến, cách tính phí và giới hạn sử dụng trước khi deploy. Giá cụ thể sẽ được gửi cùng lời mời alpha.
- **Theo dõi app ở một nơi:** xem logs, health checks và lịch sử deploy của các service trong cùng một project.

## Embra đang ở đâu?

| Trạng thái | Nội dung |
|---|---|
| Đã thử trong lab | Gate migration trên replica · restore PITR từ S3 |
| Đang làm | Build và deploy Node.js / Next.js · domain · HTTPS · CLI/MCP |
| Chưa làm | File storage · worker · queue · auth · email · realtime |
| Chưa cam kết | SLA · uptime 99.x% · autoscale |

Lab = VPS thử nghiệm của Embra, không phải app của khách. Giao diện release trên trang chủ chỉ là minh hoạ; con số chi phí trong đó là số ví dụ. Lời mời sẽ ghi rõ tính năng, stack, giới hạn, chi phí và điều kiện thử. Vị trí xử lý dữ liệu của từng dịch vụ và bên tích hợp sẽ được công bố theo phạm vi cung cấp.

## Hoàng Xuân / Founder

Mình từng phá hỏng database của công ty.

Khi xây Embra, mình luôn nghĩ về tình huống đó: app đang lỗi, mọi người chờ hệ thống hoạt động lại, còn người xử lý phải tìm xem dữ liệu nào đã mất, backup có dùng được không và restore sẽ mất bao lâu.

Với một team nhỏ, người viết code thường cũng là người deploy và xử lý sự cố. Bạn cần đưa tính năng mới lên, nhưng mỗi thay đổi database lại có thể ảnh hưởng tới dữ liệu đang chạy thật.

Đó là vấn đề mình muốn giải quyết với Embra: thấy rủi ro trước khi chạy migration, có bước review rõ ràng và chuẩn bị đường restore trước khi cần đến nó.

Embra đang được xây dựng theo hướng đó. Mình muốn cùng những team đầu tiên kiểm chứng nó trên project thử nghiệm.

Mình trực tiếp xây dựng và support. Embra hiện là dự án cá nhân, chưa có pháp nhân. [GitHub](https://github.com/hxuan190) · [LinkedIn](https://www.linkedin.com/in/hxuan190)

## Tham gia closed alpha

Tham gia waitlist tại https://embra.cloud/#join và tự xác nhận đồng ý xử lý dữ liệu. Sau khi xác nhận email, bạn sẽ được liên hệ khi có đợt alpha phù hợp. Đăng ký không tạo tài nguyên hay phát sinh phí. Chưa cần chuyển ứng dụng đang chạy sang Embra.

Khi được mời, bắt đầu với dự án thử nghiệm hoặc môi trường không quan trọng. Khả năng phục hồi, xuất dữ liệu và giới hạn hỗ trợ sẽ được xác nhận cho từng phạm vi thử.

Liên hệ: hello@embra.cloud. [Thông báo xử lý dữ liệu](https://embra.cloud/chinh-sach-du-lieu.html). [Thông tin cho agent](https://embra.cloud/llms.txt).
