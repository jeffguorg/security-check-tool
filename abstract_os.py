class AbstractOS:
    # 使用 yield 返回一条记录
    def get_usb_plugin_records(self):
        raise NotImplementedError()