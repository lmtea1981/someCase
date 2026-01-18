import sys
from typing import Any, Generator

class StreamingOutputHandler:
    """
    流输出处理器，用于优化流输出的展示效果
    """
    
    def __init__(self, stream=sys.stdout):
        """
        初始化流输出处理器
        
        Args:
            stream: 输出流，默认为sys.stdout
        """
        self.stream = stream
        self.buffer = []
    
    def write(self, content: Any) -> None:
        """
        写入流输出内容
        
        Args:
            content: 要写入的内容
        """
        if isinstance(content, str):
            # 实时输出内容
            self.stream.write(content)
            self.stream.flush()
            self.buffer.append(content)
        else:
            # 如果是其他类型，转换为字符串
            str_content = str(content)
            self.stream.write(str_content)
            self.stream.flush()
            self.buffer.append(str_content)
    
    def writelines(self, lines: Generator[str, None, None]) -> None:
        """
        写入多行流输出内容
        
        Args:
            lines: 行生成器
        """
        for line in lines:
            self.write(line)
    
    def get_buffer(self) -> str:
        """
        获取缓冲区内容
        
        Returns:
            缓冲区内容字符串
        """
        return ''.join(self.buffer)
    
    def clear_buffer(self) -> None:
        """
        清空缓冲区
        """
        self.buffer.clear()
    
    def print_divider(self, char: str = '-', length: int = 80) -> None:
        """
        打印分隔线
        
        Args:
            char: 分隔线字符，默认为'-'
            length: 分隔线长度，默认为80
        """
        divider = char * length
        self.write(f"\n{divider}\n")
    
    def print_title(self, title: str) -> None:
        """
        打印标题
        
        Args:
            title: 标题内容
        """
        self.print_divider()
        self.write(f"\n{title}\n")
        self.print_divider()
