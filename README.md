# PySemaLRParser

PSLRP is a SLR(1) parser with semantics written in pure Python.

PSLRP 是一个完全由 Python 实现的带语义计算的 SLR(1) 分析器。

## PSLRP 的特点

- 完全由 Python 实现，且不使用第三方库
- 职责单一：带语义计算的 SLR(1) 分析器
- 命名可读性强，相同含义命名相同，注释完善

## PSLRP 支持的文法

PSLRP 支持的文法满足以下条件：

1. 必须是 SLR(1) 文法
2. 不使用以下三个字符串作为符号：

- \<empty\>
- $end
- .（英文句号）

## PSLRP 的使用方法

使用 PSLRP 构造一个带语义计算的 SLR(1) 分析器需要以下步骤：

1. 声明所有终结符
2. 使用上述终结符构造文法
3. 为文法添加产生式（和语义动作）
4. 生成文法的 first 集
5. 生成文法的 follow 集
6. 生成文法的 LR 项目
7. 使用上述文法构造 SLR 分析表
8. 生成 SLR 分析表对象的分析表
9. 使用上述分析表构造 SLR 分析器
10. 构造 token 序列
11. 使用上述分析器解析 token 序列

在源码的 tests 目录下有若干个示例，可以参照它们。

## 如何处理 L- 翻译模式

1. 首先将该 L- 翻译模式改写成 S- 翻译模式（添加空产生式）
2. 然后创建一个全局字典，每个继承属性，对应字典中的一项

如果希望使用传统方法，PSLRP 也允许直接操控符号栈，但不推荐这么做。

## PSLLP

PSLLP 是一个不知道有什么用处的带语义计算的 LL(1) 递归下降子程序生成器。

### PSLLP 支持的文法

除必须是 LL(1) 文法外，其他条件与 PSLRP 相同。

请注意：在构造生成器时并不会检查是否符合条件，只有在推导时才会发现错误。

### PSLLP 的使用方法

除了无需生成 LR 项目以外，其余步骤与 PSLRP 类似。

在 tests 目录下也有它的若干示例，可以参照它们。

### PSLLP 如何处理语义计算

PSLLP 在递归下降子程序内部维护属性栈，在调用其他子程序时传入自身的属性栈。

比如说，对于产生式 N -> { B.len = N.len } B { N1.len = N.len + 1 } N1 { N.val = B.val + N1.val } 而言，它的三个语义动作被定义为三个函数，如下所示：

```python
def meet_n_bn_0(new, old):
    print('meet_n_bn_0')
    # N -> {<this>} B N
    new['B.len'] = old['N.len']


def meet_n_bn_1(new, old):
    print('meet_n_bn_1')
    # N -> B {<this>} N
    new['N.len'] = old['N.len'] + 1


def meet_n_bn_2(new, old):
    print('meet_n_bn_2')
    # N -> B N {<this>}
    old['N.val'] = new['B.val'] + new['N.val']
```