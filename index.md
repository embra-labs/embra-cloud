# Embra · Mỗi lần deploy đều có đường lui

Embra là hosting app và PostgreSQL cho developer và team nhỏ tại Việt Nam: build, deploy và theo dõi app trong cùng một project, với review thay đổi database và chuẩn bị phục hồi.

## Có phù hợp với dự án của bạn?

Bạn đang xây website, web app hoặc API; người viết code cũng là người cấu hình server và deploy. Embra hướng tới việc giảm phần vận hành bạn phải tự nối giữa app và database. Có thể bắt đầu từ frontend rồi thêm backend.

**Cập nhật 25/10/2026:** beta trả phí, nhận app production trong giới hạn từng gói; onboarding trực tiếp từng khách. Giá từ 249.000đ mỗi project mỗi tháng: [bảng giá](https://embra.cloud/bang-gia/).

[Bắt đầu ở đây](https://github.com/embra-labs/.github/blob/main/docs/start-here.md) · [Engineering](https://embra.cloud/engineering/) · [Bảng giá](https://embra.cloud/bang-gia/) · [Đăng ký](https://embra.cloud/#join) · [Hỗ trợ](https://github.com/embra-labs/.github/blob/main/SUPPORT.md)

## Có gì trong beta (cập nhật 24/10/2026)

Deploy từ GitHub qua dashboard, Embra tự build từ source. PostgreSQL riêng, review migration trước khi chạy, backup liên tục và restore theo thời điểm. Worker, cron và bucket lưu file theo từng gói. Domain riêng + HTTPS, log và metrics, CLI và MCP (`embra mcp`), tự xuất dữ liệu bằng `embra export`. Máy chủ tại TP.HCM.

Beta tập trung vào frontend, Node.js / Next.js và PostgreSQL. Chưa có: queue, auth, email, realtime (roadmap).

## Có thể kiểm chứng ngay

| Nội dung | Phạm vi bằng chứng |
| :--- | :--- |
| [So sánh nơi chạy app có Postgres](https://embra.cloud/so-sanh/) | Vercel, Supabase, Neon, Railway, Render, Mắt Bão Vibe Host, VPS và Embra; đối chiếu trang chính thức 21/10/2026 (Render, Supabase, Neon 24/10/2026) |
| [Độ trễ từ Việt Nam tới các region gần](https://embra.cloud/engineering/do-tre-viet-nam/) | Đo 22/10/2026 từ một máy, ngoài giờ cao điểm; có giới hạn phép đo |
| [Chuyển app Next.js có Postgres khỏi Vercel](https://embra.cloud/engineering/chuyen-khoi-vercel/) | Hướng dẫn thực hành: kiểm kê, build, chuyển database có diễn tập, đổi DNS; dùng được khi tự host |
| [Deploy app có Postgres](https://embra.cloud/engineering/deploy-with-postgres/) | Hướng dẫn thực hành: migration, rollback, restore và checklist tải về; dùng được khi tự host |
| [Một lần deploy ở Embra đi qua những đâu?](https://embra.cloud/engineering/how-embra-works/) | Kiến trúc đối chiếu ngày 09/10/2026: kế hoạch, migration, chuyển traffic và giới hạn phục hồi |
| [Backfill 8 triệu dòng](https://embra.cloud/engineering/backfill-8m/) | Lab 28–30/09/2026: toàn vẹn đạt trong fixture; mục tiêu latency chưa đạt |
| [backfill-demo](https://github.com/embra-labs/backfill-demo) | Fixture riêng 1.000 dòng, code + CI, kill trước/sau commit và đối chứng sai; không tái lập benchmark cũ |
| [Flow sản phẩm](https://embra.cloud/#stage) | Minh hoạ flow sản phẩm; chưa phải giao diện phát hành, không chạy trên app thật |

Các thử nghiệm dùng dữ liệu tổng hợp. Số thời gian và chi phí trong minh hoạ là ví dụ. Restore về mốc cũ có thể bỏ các lần ghi sau mốc đó; kết quả lab không phải SLA hoặc cam kết phục hồi không mất dữ liệu.

## Hoàng Xuân / Founder

Mình từng phá hỏng database của công ty.

Khi xây Embra, mình luôn nghĩ về tình huống đó: app đang lỗi, mọi người chờ hệ thống hoạt động lại, còn người xử lý phải tìm xem dữ liệu nào đã mất, backup có dùng được không và restore sẽ mất bao lâu.

Với một team nhỏ, người viết code thường cũng là người deploy và xử lý sự cố. Bạn cần đưa tính năng mới lên, nhưng mỗi thay đổi database lại có thể ảnh hưởng tới dữ liệu đang chạy thật.

Đó là vấn đề mình muốn giải quyết với Embra: thấy rủi ro trước khi chạy migration, có bước review rõ ràng và chuẩn bị đường restore trước khi cần đến nó.

Mình kiểm tra riêng tính toàn vẹn dữ liệu và ảnh hưởng đến app. Trong [lab backfill 8 triệu dòng](https://embra.cloud/engineering/backfill-8m/), toàn vẹn đạt trong fixture nhưng latency chưa đạt mục tiêu. Kết quả và giới hạn phép đo được công bố để người đọc đối chiếu.

Mình trực tiếp xây dựng và support. Embra hiện là dự án cá nhân, chưa có pháp nhân. [GitHub](https://github.com/hxuan190) · [LinkedIn](https://www.linkedin.com/in/hxuan190)

## Quyền kiểm soát và hỗ trợ

Rollback code và restore database là hai việc khác nhau. Restore về mốc cũ có thể bỏ các lần ghi sau mốc đó.

Owner tự xuất app và dữ liệu bằng `embra export`. Mỗi lần đội Embra truy cập log, metrics hay database của bạn để hỗ trợ đều được ghi lại kèm lý do.

Bạn chịu trách nhiệm code và logic ứng dụng. Hoàng Xuân trực tiếp support; hỗ trợ qua hello@embra.cloud; beta chưa có SLA. [Hỗ trợ / báo lỗi](https://github.com/embra-labs/.github/blob/main/SUPPORT.md).

## Bắt đầu với beta

1. [Đăng ký quan tâm](https://embra.cloud/#join) và xác nhận email; bước này chưa cấp quyền truy cập.
2. Embra liên hệ để xác nhận stack, gói phù hợp ([bảng giá](https://embra.cloud/bang-gia/)) và cách hỗ trợ.
3. Trước khi thử, bạn nhận hướng dẫn truy cập, phiên bản được hỗ trợ và cách lấy dữ liệu ra khi kết thúc.

Đăng ký không tạo tài nguyên hoặc phát sinh phí. Beta nhận app production trong giới hạn từng gói. Giá: Start 249.000đ, Build 399.000đ, Grow 749.000đ mỗi project mỗi tháng ([bảng giá](https://embra.cloud/bang-gia/)); chưa xuất hoá đơn VAT vì chưa có pháp nhân. Máy chủ đặt tại Việt Nam.

[Changelog](https://github.com/embra-labs/.github/blob/main/docs/changelog.md) · [Hỗ trợ / báo lỗi](https://github.com/embra-labs/.github/blob/main/SUPPORT.md) · [hello@embra.cloud](mailto:hello@embra.cloud) · [Thông báo xử lý dữ liệu](https://embra.cloud/chinh-sach-du-lieu.html) · [Thông tin cho agent](https://embra.cloud/llms.txt)
