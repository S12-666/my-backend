import json
from ..utils import executeSql

class SendPredictionController:
    def __init__(self, para):
        self.para = para
        self.upid = para.get('upid')
        self.msg = para.get('msg')
        self.label = para.get('label')

    def run(self):
        if not self.upid:
            return {"success": False, "message": "Missing UPID"}

        try:
            pred_label_json = json.dumps(self.label)
            safe_msg = self.msg.replace("'", "''") if self.msg else ""

            sql = f"""
                        UPDATE "app"."deba_dump_properties_copy1"
                        SET 
                            pred_label = '{pred_label_json}'::jsonb,
                            msg = '{safe_msg}'
                        WHERE upid = '{self.upid}';
                """

            success, info = executeSql(sql)

            if success:
                return {
                    "success": True,
                    "message": "数据保存成功",
                    "debug_info": info
                }
            else:
                return {
                    "success": False,
                    "message": f"数据库保存失败: {info}"
                }
        except Exception as e:
            return {"success": False, "message": f"处理逻辑异常: {str(e)}"}
