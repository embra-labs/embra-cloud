# Deploy app có Postgres: kiểm gì trước khi chuyển sang bản mới?

*Embra Engineering · Xuất bản trên website 09/10/2026 · Phát triển từ guide GitHub ngày 08/10/2026.*

Bài này giúp bạn chuẩn bị một lần deploy app có Postgres: dữ liệu nào phải giữ lại, code cũ còn chạy được sau migration không, và cần kiểm gì nếu phải restore. Dùng được khi tự host hoặc dùng nền tảng khác; không cần tài khoản Embra.

Các bước thực hành dùng môi trường test và dữ liệu tổng hợp. [Tải checklist để ghi kết quả](https://embra.cloud/engineering/deploy-with-postgres/checklist.md).

Bạn có một app nhận đơn hàng. Trên máy cá nhân, trang web mở được, API ghi đơn
vào Postgres và ảnh được lưu vào một thư mục. Để đưa app lên mạng, hãy xác định
phần nào có thể tạo lại và phần nào phải sống qua lần thay phiên bản tiếp theo.

## Vẽ đường đi của một đơn hàng

```text
Trình duyệt → API → Postgres: mã đơn, trạng thái, tham chiếu ảnh
                 → nơi lưu file: nội dung ảnh
                 → hàng đợi, nếu có → worker gửi thông báo
```

Frontend hiển thị giao diện. API xử lý yêu cầu và quyền truy cập. Database giữ
dữ liệu có cấu trúc. Nơi lưu file giữ nội dung ảnh. Worker làm việc có thể xử lý
sau khi API trả lời. Một ứng dụng nhỏ có thể gộp frontend và API trong một
process; chỉ tách thêm khi công việc cần đến.

## Kiểm tra bốn điều trước lần deploy tiếp theo

**1. Khi thay container, dữ liệu nào còn?**

File trong lớp ghi của container có thể mất khi container bị xóa và tạo lại.
Ảnh người dùng cần nơi lưu bền vững như volume được quản lý hoặc object storage.
Database cũng cần storage bền vững. Việc app hiện tại đọc được ảnh chưa chứng
minh ảnh sẽ còn sau deploy. Thử thay container trong môi trường test rồi đọc
lại cùng một đơn và ảnh đã tạo trước đó. Xem cơ chế lưu trữ trong [tài liệu Docker](https://docs.docker.com/engine/storage/).

**2. Phiên bản mới đang kết nối tới môi trường nào?**

Ghi rõ cấu hình cho test và production: endpoint database, nơi lưu file và các
dịch vụ bên ngoài. Không in mật khẩu hoặc token để kiểm tra. Dùng tên môi
trường và định danh cấu hình đã che dữ liệu nhạy cảm. Kiểm cả cấu hình lúc build
và lúc chạy nếu framework của bạn sử dụng hai giai đoạn đó.

**3. App trả HTTP 200 có nghĩa là tạo được đơn không?**

Một trang health chỉ trả chuỗi “OK” có thể vẫn hoạt động khi database mất kết
nối. Dùng readiness phù hợp để kiểm tra phụ thuộc cần thiết, và một bài thử
tạo/đọc đơn bằng dữ liệu tổng hợp trong môi trường test. Không tạo đơn thật
hoặc gửi email cho khách mỗi lần hệ thống gọi healthcheck.

**4. Nếu phiên bản mới lỗi, quay lại code cũ có đủ không?**

Code cũ phải đọc được schema và dữ liệu hiện tại. Nếu migration đã xóa cột mà
code cũ dùng, quay lại image cũ không tự mang cột đó về. Trước deploy, kiểm tra
tính tương thích của thay đổi dữ liệu và đường phục hồi riêng.

## Tách đổi schema thành các lần deploy có đường quay lại

Giả sử bản A đọc cột `legacy_ref`. Bản B chuyển sang `external_ref`. Nếu B xoá ngay cột cũ, rollback về A vẫn lỗi vì database không còn như lúc A được deploy.

Thay đổi này có thể chia thành ba giai đoạn. Đây là cách tổ chức công việc, không phải một chuỗi SQL áp dụng nguyên xi cho mọi app:

| Giai đoạn | Thay đổi | Điều cần kiểm trước khi đi tiếp |
| :--- | :--- | :--- |
| Thêm cấu trúc mới | Thêm `external_ref`, giữ `legacy_ref`. Deploy bản chuyển tiếp có thể làm việc với cả hai. | Code cũ vẫn chạy; các lần ghi mới giữ hai trường nhất quán theo quy tắc của app. |
| Chuyển dữ liệu và nơi đọc | Điền dữ liệu cũ theo lô, rồi chuyển phần đọc sang trường mới. | Dữ liệu đã chuyển đúng; không bỏ sót các dòng tạo hoặc sửa trong lúc backfill; mọi app và worker đang chạy đều tương thích. |
| Bỏ cấu trúc cũ | Dừng dùng `legacy_ref`, sau đó mới xoá khi đã xác nhận không còn nơi đọc hoặc ghi vào nó. | Không còn phiên bản cũ, tác vụ nền hay công cụ báo cáo phụ thuộc cột này. Mốc rollback cho phép đã được cập nhật. |

Phần ghi đồng thời phải được thiết kế theo app. Không thể chỉ chép hết dữ liệu cũ rồi coi các dòng được tạo trong lúc đó sẽ tự đúng. Nếu hai cột cùng nằm trong một database, có thể cập nhật chúng trong cùng transaction; nếu có hệ thống bên ngoài, cần cách xử lý riêng khi một bên thành công còn bên kia thất bại.

Cách chia giai đoạn này thường được gọi là *expand–contract*. Nó giúp giữ một khoảng tương thích giữa các phiên bản. Nó không loại bỏ lock hay chi phí chạy migration: PostgreSQL vẫn lấy các loại lock khác nhau tuỳ câu lệnh. Hãy xem [cơ chế locking của PostgreSQL](https://www.postgresql.org/docs/18/explicit-locking.html) và diễn tập với kích thước dữ liệu, truy vấn đồng thời phù hợp.

## Bài thực hành nhỏ

Trên môi trường test với dữ liệu giả:

1. Tạo một đơn có mã thử riêng, ví dụ `DEPLOY-TEST-001`; ghi lại trạng thái và tổng tiền. Nếu app có upload, lưu một ảnh và checksum của ảnh.
2. Thay container app bằng phiên bản tiếp theo.
3. Đọc lại đúng đơn đó và đối chiếu từng trường; nếu có upload, tải ảnh và so checksum. Không chỉ kiểm tổng số dòng.
4. Thử một phiên bản có readiness lỗi và quan sát có traffic đi vào nó không.
5. Quay lại phiên bản trước nếu schema tương thích, rồi đọc lại dữ liệu.

Bài này kiểm tính liên tục của dữ liệu qua deploy. Để kiểm backup, cần một bài
khác: phục hồi vào môi trường cách ly và đối chiếu dữ liệu. Backup tồn tại và
backup phục hồi được là hai điều cần kiểm riêng.

## Khi nào nên dừng deploy?

Trước khi chạy, ghi lại mức lỗi và latency bình thường của app, mức tăng có thể chấp nhận, thời gian quan sát và người quyết định dừng. Ngưỡng phải phù hợp với ứng dụng của bạn; bài này không đưa ra một con số chung cho mọi hệ thống.

Dừng để kiểm tra khi gặp một trong những tình huống sau:

- **Không chắc app đang trỏ vào đâu.** Chưa xác nhận database, nơi lưu file hoặc cấu hình môi trường thì chưa chạy migration.
- **Migration chờ lock quá lâu hoặc làm app chậm rõ rệt.** Kiểm tra truy vấn đang giữ lock và ảnh hưởng đến người dùng trước khi thử lại. Đừng chỉ tăng timeout để bỏ qua triệu chứng.
- **Mất kết nối quanh commit, chưa biết migration đã áp hay chưa.** Đối chiếu trạng thái database và lịch sử thực thi trước khi chạy lại. Một lỗi phía client chưa đủ để kết luận transaction thất bại.
- **Readiness không đạt, dữ liệu đối chiếu sai hoặc lỗi tăng sau khi đổi bản.** Giữ hoặc chuyển request về bản đã kiểm chứng nếu schema còn tương thích. Nếu chưa biết có tương thích không, dừng các thay đổi tiếp theo và làm theo phương án xử lý sự cố đã chuẩn bị.

Ghi riêng trạng thái code và database. “App mới chưa chạy” khác với “migration chưa áp”. Nếu migration đã commit, việc chuyển request về app cũ không hoàn tác phần dữ liệu đó. [Bài kiến trúc Embra](https://embra.cloud/engineering/how-embra-works/) giải thích một cách biểu diễn hai trạng thái này trong luồng deploy.

## Diễn tập phục hồi riêng

Có storage bền vững chưa chứng minh bạn phục hồi được khi mất dữ liệu. Với một bản backup, hãy thử restore vào database riêng, kết nối bản app thử vào đó và đọc lại mã đơn đã ghi nhận. Nếu app lưu ảnh bên ngoài Postgres, kiểm cả file tương ứng: backup database không tự chứa những file đó.

Với SQL dump, cần chuẩn bị các role/quyền phù hợp và kiểm lỗi restore, không chỉ nhìn thấy file backup. Xem [backup và restore bằng SQL dump của PostgreSQL](https://www.postgresql.org/docs/18/backup-dump.html).

Nếu dùng phục hồi theo thời điểm (PITR), cần base backup và chuỗi WAL cần thiết để tới được mốc phục hồi. Chọn rõ mốc thời gian, kiểm dữ liệu trước/sau mốc và ghi lại phần ghi mới không có trong database đã phục hồi. Đọc [hướng dẫn PITR của PostgreSQL](https://www.postgresql.org/docs/18/continuous-archiving.html) cho cách cấu hình và thực hiện; bài này không thay runbook của hệ thống bạn.

## Ghi kết quả trước khi gọi là sẵn sàng

[Checklist Markdown tải về](https://embra.cloud/engineering/deploy-with-postgres/checklist.md) có cùng các mục dưới đây để bạn điền cho từng lần thử.

Bảng dưới là mẫu để tự điền, không phải kết quả thử nghiệm của Embra. Ghi ngày, phiên bản app/schema và môi trường cùng kết quả. “Chưa chạy” khác với “đạt”.

| Phép kiểm | Bằng chứng cần lưu | Kết quả của bạn |
| :--- | :--- | :--- |
| Thay container | Đơn thử vẫn có đúng trạng thái/tổng tiền; checksum ảnh khớp nếu có | Chưa chạy |
| Cấu hình môi trường | App trỏ đúng DB/storage thử; không lộ credential | Chưa chạy |
| Phiên bản chưa sẵn sàng | Request không được chuyển sang bản chưa qua readiness | Chưa chạy |
| Quay lại code cũ | Bản cũ chạy được với schema hiện tại trong phạm vi đã thử | Chưa chạy |
| Restore backup | App đọc được đơn thử từ DB phục hồi riêng; file tham chiếu tồn tại nếu có | Chưa chạy |
| Mốc và thời gian phục hồi | Ghi mốc dữ liệu, thời gian thực hiện và phần dữ liệu không được khôi phục | Chưa chạy |

Bộ kiểm này giúp tìm các lỗ hổng thường gặp, chưa chứng minh hệ thống chịu được mọi sự cố hoặc mọi mức tải. Thời gian restore của database thử nhỏ không phải cam kết thời gian cho database production.

## Đọc tiếp theo vấn đề bạn đang gặp

- **Muốn hiểu một nền tảng phối hợp app và database thế nào:** [Một lần deploy ở Embra đi qua những đâu?](https://embra.cloud/engineering/how-embra-works/).
- **Đang chuẩn bị backfill bảng lớn:** [Backfill tám triệu dòng: dữ liệu đúng, nhưng latency không đạt](https://embra.cloud/engineering/backfill-8m/). Bài thử cho thấy vì sao dữ liệu đúng và app đáp ứng được là hai tiêu chí riêng.
- **Muốn tự kiểm cơ chế tiếp tục sau ngắt:** [backfill-demo](https://github.com/embra-labs/backfill-demo), ví dụ độc lập 1.000 dòng, có đối chứng sai.

Embra đang xây dựng hosting app và PostgreSQL, chuẩn bị closed alpha theo lời mời. Guide này là hướng dẫn chung, không phải danh sách tính năng đã phát hành. Xem [phạm vi hiện tại](https://embra.cloud/#trang-thai) nếu muốn tìm hiểu sản phẩm.
