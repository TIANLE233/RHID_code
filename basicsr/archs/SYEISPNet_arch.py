import torch
import torch.nn as nn
from basicsr.utils.registry import ARCH_REGISTRY


class ConvRep5(nn.Module):
    def __init__(self, in_channels, out_channels, rep_scale=4):
        super(ConvRep5, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.conv = nn.Conv2d(in_channels, out_channels * rep_scale, 5, 1, 2)
        self.conv_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, 5, 1, 2),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv1 = nn.Conv2d(in_channels, out_channels * rep_scale, 1)
        self.conv1_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, 1),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv2 = nn.Conv2d(in_channels, out_channels * rep_scale, 3, 1, 1)
        self.conv2_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, 3, 1, 1),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv_crossh = nn.Conv2d(in_channels, out_channels * rep_scale, (3, 1), 1, (1, 0))
        self.conv_crossh_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, (3, 1), 1, (1, 0)),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv_crossv = nn.Conv2d(in_channels, out_channels * rep_scale, (1, 3), 1, (0, 1))
        self.conv_crossv_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, (1, 3), 1, (0, 1)),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv_out = nn.Conv2d(out_channels * rep_scale * 10, out_channels, 1)

    def forward(self, inp):
        x = torch.cat(
            [self.conv(inp),
             self.conv1(inp),
             self.conv2(inp),
             self.conv_crossh(inp),
             self.conv_crossv(inp),
             self.conv_bn(inp),
             self.conv1_bn(inp),
             self.conv2_bn(inp),
             self.conv_crossh_bn(inp),
             self.conv_crossv_bn(inp)],
            1
        )

        out = self.conv_out(x)

        return out

    def slim(self):
        conv_weight = self.conv.weight
        conv_bias = self.conv.bias
        conv1_weight = self.conv1.weight
        conv1_bias = self.conv1.bias
        conv1_weight = nn.functional.pad(conv1_weight, (2, 2, 2, 2))
        conv2_weight = self.conv2.weight
        conv2_weight = nn.functional.pad(conv2_weight, (1, 1, 1, 1))
        conv2_bias = self.conv2.bias
        conv_crossv_weight = self.conv_crossv.weight
        conv_crossv_weight = nn.functional.pad(conv_crossv_weight, (1, 1, 2, 2))
        conv_crossv_bias = self.conv_crossv.bias
        conv_crossh_weight = self.conv_crossh.weight
        conv_crossh_weight = nn.functional.pad(conv_crossh_weight, (2, 2, 1, 1))
        conv_crossh_bias = self.conv_crossh.bias
        conv1_bn_weight = self.conv1_bn[0].weight
        conv1_bn_weight = nn.functional.pad(conv1_bn_weight, (2, 2, 2, 2))
        conv2_bn_weight = self.conv2_bn[0].weight
        conv2_bn_weight = nn.functional.pad(conv2_bn_weight, (1, 1, 1, 1))
        conv_crossv_bn_weight = self.conv_crossv_bn[0].weight
        conv_crossv_bn_weight = nn.functional.pad(conv_crossv_bn_weight, (1, 1, 2, 2))
        conv_crossh_bn_weight = self.conv_crossh_bn[0].weight
        conv_crossh_bn_weight = nn.functional.pad(conv_crossh_bn_weight, (2, 2, 1, 1))
        bn = self.conv_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv_bn_weight = self.conv_bn[0].weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_bn_weight = conv_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_bn_bias = self.conv_bn[0].bias * k + b
        conv_bn_bias = conv_bn_bias * bn.weight + bn.bias
        bn = self.conv1_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv1_bn_weight = conv1_bn_weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv1_bn_weight = conv1_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv1_bn_bias = self.conv1_bn[0].bias * k + b
        conv1_bn_bias = conv1_bn_bias * bn.weight + bn.bias
        bn = self.conv2_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv2_bn_weight = conv2_bn_weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv2_bn_weight = conv2_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv2_bn_bias = self.conv2_bn[0].bias * k + b
        conv2_bn_bias = conv2_bn_bias * bn.weight + bn.bias
        bn = self.conv_crossv_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv_crossv_bn_weight = conv_crossv_bn_weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossv_bn_weight = conv_crossv_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossv_bn_bias = self.conv_crossv_bn[0].bias * k + b
        conv_crossv_bn_bias = conv_crossv_bn_bias * bn.weight + bn.bias
        bn = self.conv_crossh_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv_crossh_bn_weight = conv_crossh_bn_weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossh_bn_weight = conv_crossh_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossh_bn_bias = self.conv_crossh_bn[0].bias * k + b
        conv_crossh_bn_bias = conv_crossh_bn_bias * bn.weight + bn.bias
        weight = torch.cat(
            [conv_weight, conv1_weight, conv2_weight,
             conv_crossh_weight, conv_crossv_weight,
             conv_bn_weight, conv1_bn_weight, conv2_bn_weight,
             conv_crossh_bn_weight, conv_crossv_bn_weight],
            0
        )
        weight_compress = self.conv_out.weight.squeeze()
        weight = torch.matmul(weight_compress, weight.permute([2, 3, 0, 1])).permute([2, 3, 0, 1])
        bias_ = torch.cat(
            [conv_bias, conv1_bias, conv2_bias,
             conv_crossh_bias, conv_crossv_bias,
             conv_bn_bias, conv1_bn_bias, conv2_bn_bias,
             conv_crossh_bn_bias, conv_crossv_bn_bias],
            0
        )
        bias = torch.matmul(weight_compress, bias_)
        if isinstance(self.conv_out.bias, torch.Tensor):
            bias = bias + self.conv_out.bias
        return weight, bias


class ConvRep3(nn.Module):
    def __init__(self, in_channels, out_channels, rep_scale=4):
        super(ConvRep3, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.conv = nn.Conv2d(in_channels, out_channels * rep_scale, 3, 1, 1)
        self.conv_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, 3, 1, 1),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv1 = nn.Conv2d(in_channels, out_channels * rep_scale, 1)
        self.conv1_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, 1),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv_crossh = nn.Conv2d(in_channels, out_channels * rep_scale, (3, 1), 1, (1, 0))
        self.conv_crossh_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, (3, 1), 1, (1, 0)),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv_crossv = nn.Conv2d(in_channels, out_channels * rep_scale, (1, 3), 1, (0, 1))
        self.conv_crossv_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, (1, 3), 1, (0, 1)),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv_out = nn.Conv2d(out_channels * rep_scale * 8, out_channels, 1)

    def forward(self, inp):
        x = torch.cat(
            [self.conv(inp),
             self.conv1(inp),
             self.conv_crossh(inp),
             self.conv_crossv(inp),
             self.conv_bn(inp),
             self.conv1_bn(inp),
             self.conv_crossh_bn(inp),
             self.conv_crossv_bn(inp)],
            1
        )

        out = self.conv_out(x)

        return out

    def slim(self):
        conv_weight = self.conv.weight
        conv_bias = self.conv.bias
        conv1_weight = self.conv1.weight
        conv1_bias = self.conv1.bias
        conv1_weight = nn.functional.pad(conv1_weight, (1, 1, 1, 1))
        conv_crossv_weight = self.conv_crossv.weight
        conv_crossv_weight = nn.functional.pad(conv_crossv_weight, (0, 0, 1, 1))
        conv_crossv_bias = self.conv_crossv.bias
        conv_crossh_weight = self.conv_crossh.weight
        conv_crossh_weight = nn.functional.pad(conv_crossh_weight, (1, 1, 0, 0))
        conv_crossh_bias = self.conv_crossh.bias
        conv1_bn_weight = self.conv1_bn[0].weight
        conv1_bn_weight = nn.functional.pad(conv1_bn_weight, (1, 1, 1, 1))
        conv_crossv_bn_weight = self.conv_crossv_bn[0].weight
        conv_crossv_bn_weight = nn.functional.pad(conv_crossv_bn_weight, (0, 0, 1, 1))
        conv_crossh_bn_weight = self.conv_crossh_bn[0].weight
        conv_crossh_bn_weight = nn.functional.pad(conv_crossh_bn_weight, (1, 1, 0, 0))
        bn = self.conv_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv_bn_weight = self.conv_bn[0].weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_bn_weight = conv_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_bn_bias = self.conv_bn[0].bias * k + b
        conv_bn_bias = conv_bn_bias * bn.weight + bn.bias
        bn = self.conv1_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv1_bn_weight = conv1_bn_weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv1_bn_weight = conv1_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv1_bn_bias = self.conv1_bn[0].bias * k + b
        conv1_bn_bias = conv1_bn_bias * bn.weight + bn.bias
        bn = self.conv_crossv_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv_crossv_bn_weight = conv_crossv_bn_weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossv_bn_weight = conv_crossv_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossv_bn_bias = self.conv_crossv_bn[0].bias * k + b
        conv_crossv_bn_bias = conv_crossv_bn_bias * bn.weight + bn.bias
        bn = self.conv_crossh_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv_crossh_bn_weight = conv_crossh_bn_weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossh_bn_weight = conv_crossh_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_crossh_bn_bias = self.conv_crossh_bn[0].bias * k + b
        conv_crossh_bn_bias = conv_crossh_bn_bias * bn.weight + bn.bias
        weight = torch.cat(
            [conv_weight, conv1_weight,
             conv_crossh_weight, conv_crossv_weight,
             conv_bn_weight, conv1_bn_weight,
             conv_crossh_bn_weight, conv_crossv_bn_weight],
            0
        )
        weight_compress = self.conv_out.weight.squeeze()
        weight = torch.matmul(weight_compress, weight.permute([2, 3, 0, 1])).permute([2, 3, 0, 1])
        bias_ = torch.cat(
            [conv_bias, conv1_bias,
             conv_crossh_bias, conv_crossv_bias,
             conv_bn_bias, conv1_bn_bias,
             conv_crossh_bn_bias, conv_crossv_bn_bias],
            0
        )
        bias = torch.matmul(weight_compress, bias_)
        if isinstance(self.conv_out.bias, torch.Tensor):
            bias = bias + self.conv_out.bias
        return weight, bias


class ConvRepPoint(nn.Module):
    def __init__(self, in_channels, out_channels, rep_scale=4):
        super(ConvRepPoint, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.conv = nn.Conv2d(in_channels, out_channels * rep_scale, 1)
        self.conv_bn = nn.Sequential(
            nn.Conv2d(in_channels, out_channels * rep_scale, 1),
            nn.BatchNorm2d(out_channels * rep_scale)
        )
        self.conv_out = nn.Conv2d(out_channels * rep_scale * 2, out_channels, 1)

    def forward(self, inp):
        x = torch.cat([self.conv(inp), self.conv_bn(inp)], 1)
        out = self.conv_out(x)
        return out

    def slim(self):
        conv_weight = self.conv.weight
        conv_bias = self.conv.bias
        bn = self.conv_bn[1]
        k = 1 / (bn.running_var + bn.eps) ** .5
        b = - bn.running_mean / (bn.running_var + bn.eps) ** .5
        conv_bn_weight = self.conv_bn[0].weight * k.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_bn_weight = conv_bn_weight * bn.weight.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        conv_bn_bias = self.conv_bn[0].bias * k + b
        conv_bn_bias = conv_bn_bias * bn.weight + bn.bias
        weight = torch.cat([conv_weight, conv_bn_weight], 0)
        weight_compress = self.conv_out.weight.squeeze()
        weight = torch.matmul(weight_compress, weight.permute([2, 3, 0, 1])).permute([2, 3, 0, 1])
        bias = torch.cat([conv_bias, conv_bn_bias], 0)
        bias = torch.matmul(weight_compress, bias)
        if isinstance(self.conv_out.bias, torch.Tensor):
            bias = bias + self.conv_out.bias
        return weight, bias


class QuadraticConnectionUnit(nn.Module):
    def __init__(self, block1, block2, channels):
        super(QuadraticConnectionUnit, self).__init__()
        self.block1 = block1
        self.block2 = block2
        self.scale = 0.1
        self.bias = nn.Parameter(torch.randn((1, channels, 1, 1)))

    def forward(self, x):
        return self.scale * self.block1(x) * self.block2(x) + self.bias


class QuadraticConnectionUnitS(nn.Module):
    def __init__(self, block1, block2, channels):
        super(QuadraticConnectionUnitS, self).__init__()
        self.block1 = block1
        self.block2 = block2
        self.bias = nn.Parameter(torch.randn((1, channels, 1, 1)))

    def forward(self, x):
        return self.block1(x) * self.block2(x) + self.bias


class AdditionFusion(nn.Module):
    def __init__(self, addend1, addend2, channels):
        super(AdditionFusion, self).__init__()
        self.addend1 = addend1
        self.addend2 = addend2
        self.bias = nn.Parameter(torch.randn((1, channels, 1, 1)))

    def forward(self, x):
        return self.addend1(x) + self.addend2(x) + self.bias


class AdditionFusionS(nn.Module):
    def __init__(self, addend1, addend2, channels):
        super(AdditionFusionS, self).__init__()
        self.addend1 = addend1
        self.addend2 = addend2
        self.bias = nn.Parameter(torch.randn((1, channels, 1, 1)))

    def forward(self, x):
        return self.addend1(x) + self.addend2(x) + self.bias


class DropBlock(nn.Module):
    def __init__(self, block_size, p=0.5):
        super(DropBlock, self).__init__()
        self.block_size = block_size
        self.p = p / block_size / block_size

    def forward(self, x):
        mask = 1 - (torch.rand_like(x[:, :1]) >= self.p).float()
        mask = nn.functional.max_pool2d(mask, self.block_size, 1, self.block_size // 2)
        return x * (1 - mask)


class ResBlock(nn.Module):
    def __init__(self, num_feat=4, rep_scale=4):
        super(ResBlock, self).__init__()
        self.conv1 = ConvRep3(num_feat, num_feat, rep_scale=rep_scale)
        self.conv2 = ConvRep3(num_feat, num_feat, rep_scale=rep_scale)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = x
        out = self.conv2(self.relu(self.conv1(x)))
        return identity + out


class ResBlockS(nn.Module):
    def __init__(self, num_feat=4):
        super(ResBlockS, self).__init__()
        self.conv1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1, bias=True)
        self.conv2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1, bias=True)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = x
        out = self.conv2(self.relu(self.conv1(x)))
        return identity + out


@ARCH_REGISTRY.register()
class SYEISPNet(nn.Module):
    def __init__(self, upscale: int, num_in_ch: int, num_out_ch: int, task: str,
                 channels, rep_scale=4):
        super(SYEISPNet, self).__init__()
        self.channels = channels
        self.head = QuadraticConnectionUnit(
            nn.Sequential(
                ConvRep5(4, channels, rep_scale=rep_scale),
                nn.PReLU(channels),
                ConvRep3(channels, channels, rep_scale=rep_scale)
            ),
            ConvRep5(4, channels, rep_scale=rep_scale),
            channels
        )
        self.body = QuadraticConnectionUnit(
            ConvRep3(channels, 12, rep_scale=rep_scale),
            ConvRepPoint(channels, 12, rep_scale=rep_scale),
            12
        )
        self.att = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            ConvRepPoint(12, 12, rep_scale=rep_scale),
            nn.PReLU(12),
            ConvRepPoint(12, 12, rep_scale=rep_scale),
            nn.Sigmoid()
        )
        self.tail = nn.Sequential(nn.PixelShuffle(2), ConvRep3(3, 3, rep_scale=rep_scale))
        # self.tail_warm = ConvRep3(12, 4, rep_scale=rep_scale)
        # self.drop = DropBlock(3)

    def forward(self, x):
        x = self.head(x)
        x = self.body(x)
        x = self.att(x) * x
        return self.tail(x)

@ARCH_REGISTRY.register()
class SYEISPNet_noise(nn.Module):
    def __init__(self, upscale: int, num_in_ch: int, num_out_ch: int, task: str,
                 channels, rep_scale=4):
        super(SYEISPNet_noise, self).__init__()
        self.channels = channels
        self.head = QuadraticConnectionUnit(
            nn.Sequential(
                ConvRep5(4, channels - 1, rep_scale=rep_scale),
                nn.PReLU(channels-1),
                ConvRep3(channels-1, channels-1, rep_scale=rep_scale)
            ),
            ConvRep5(4, channels-1, rep_scale=rep_scale),
            channels-1
        )
        self.body = QuadraticConnectionUnit(
            ConvRep3(channels, 12, rep_scale=rep_scale),
            ConvRepPoint(channels, 12, rep_scale=rep_scale),
            12
        )
        self.att = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            ConvRepPoint(12, 12, rep_scale=rep_scale),
            nn.PReLU(12),
            ConvRepPoint(12, 12, rep_scale=rep_scale),
            nn.Sigmoid()
        )
        self.tail = nn.Sequential(nn.PixelShuffle(2), ConvRep3(3, 3, rep_scale=rep_scale))
        # self.tail_warm = ConvRep3(12, 4, rep_scale=rep_scale)
        # self.drop = DropBlock(3)

    def forward(self, x, noise_tensor):
        h = self.head(x)
        B, C, H, W = h.shape
        noise_map = noise_tensor.view(B,1,1,1).expand(B, 1, H, W)
        h_noise = torch.cat([h, noise_map], dim=1)

        # x = self.head(h_noise)
        x = self.body(h_noise)
        x = self.att(x) * x
        return self.tail(x)

@ARCH_REGISTRY.register()
class SYEISPNetS(nn.Module):
    def __init__(self, upscale: int, num_in_ch: int, num_out_ch: int, task: str,
                 channels, rep_scale=4):
        super(SYEISPNetS, self).__init__()
        self.head = QuadraticConnectionUnitS(
            nn.Sequential(
                nn.Conv2d(4, channels, 5, 1, 2),
                nn.PReLU(channels),
                nn.Conv2d(channels, channels, 3, 1, 1)
            ),
            nn.Conv2d(4, channels, 5, 1, 2),
            channels
        )
        self.body = QuadraticConnectionUnitS(
            nn.Conv2d(channels, channels, 3, 1, 1),
            nn.Conv2d(channels, channels, 1, ),
            12
        )
        self.att = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(12, 12, 1),
            nn.PReLU(12),
            nn.Conv2d(12, 12, 1),
            nn.Sigmoid()
        )
        self.tail = nn.Sequential(nn.PixelShuffle(2), nn.Conv2d(3, 3, 3, 1, 1))

    def forward(self, x, n):
        x = self.head(x)
        x = self.body(x)
        x = self.att(x) * x
        return self.tail(x)


if __name__ == '__main__':
    def count_parameters(model):
        return sum(p.numel() for p in model.parameters() if p.requires_grad)

    net = SYEISPNetS(channels=12)
    print(count_parameters(net))

    data = torch.randn(1, 4, 224, 224)
    print(net(data).size())